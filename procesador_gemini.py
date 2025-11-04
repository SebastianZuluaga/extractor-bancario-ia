"""Procesamiento de extractos bancarios asistido por Gemini."""

from __future__ import annotations

import io
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import fitz  # PyMuPDF
import google.generativeai as genai
import pandas as pd
from PIL import Image
from pikepdf import Pdf

from logging_utils import configurar_logger


logger, _ = configurar_logger("app.procesador")


PromptDict = Dict[str, str]
LogCallback = Callable[[str], None]
ProgresoCallback = Callable[[float, Optional[str]], None]


_PROMPTS: PromptDict = {
    "bancolombia": """
Analiza el siguiente extracto bancario de Bancolombia y produce únicamente un
JSON válido con todas las transacciones.

Incluye las columnas: fecha, descripcion, sucursal, dcto, valor y saldo. Si una
columna no existe en la página déjala vacía. No incluyas totales parciales ni
textos descriptivos adicionales.

Formato esperado:
{"transacciones": [{"fecha":"","descripcion":"","sucursal":"","dcto":"","valor":"","saldo":""}]}

Responde solo con el JSON.
""",
    "nu": """
Extrae el detalle de movimientos de la tarjeta Nu. Entrega exclusivamente un
JSON válido con todas las filas encontradas usando las claves: fecha,
descripcion, valor, cuotas, valor_del_mes, interes_mes, total_pagar, restante.

Formato esperado:
{"transacciones": [{"fecha":"","descripcion":"","valor":"","cuotas":"","valor_del_mes":"","interes_mes":"","total_pagar":"","restante":""}]}

No incluyas mensajes adicionales.
""",
    "rappi": """
Procesa el extracto de tarjeta Davivienda (Rappi) y responde únicamente con un
JSON válido con las claves: tarjeta, fecha, descripcion, valor_transaccion,
capital_facturado, cuotas, capital_pendiente, tasa_mv y tasa_ea.

Formato esperado:
{"transacciones": [{"tarjeta":"","fecha":"","descripcion":"","valor_transaccion":"","capital_facturado":"","cuotas":"","capital_pendiente":"","tasa_mv":"","tasa_ea":""}]}

No agregues texto adicional ni comentarios.
""",
}


# Categorías propuestas para clasificación de gastos
_CATEGORIAS_GASTO = [
    "Alimentación y Supermercado",
    "Transporte y Movilidad",
    "Hogar y Servicios",
    "Entretenimiento y Otros",
]


def _normalizar_banco(nombre_archivo: str) -> str:
    nombre = nombre_archivo.lower()
    if "nu" in nombre:
        return "nu"
    if "credit_card" in nombre or "rappi" in nombre or "davivienda" in nombre:
        return "rappi"
    return "bancolombia"


def _limpiar_salida_json(texto: str) -> Dict[str, List[Dict[str, str]]]:
    """Normaliza la respuesta de Gemini a un diccionario con clave 'transacciones'."""

    texto = texto.strip()
    if texto.startswith("```"):
        secciones = texto.split("```")
        if len(secciones) >= 2:
            contenido = secciones[1]
            if contenido.lstrip().startswith("json"):
                contenido = contenido.lstrip()[4:]
            texto = contenido.strip()

    # Intentar cargar JSON; algunos modelos devuelven arrays o objetos sin 'transacciones'
    try:
        data = json.loads(texto)
    except Exception:
        # Fallback: recortar hasta último cierre si hay ruido al final
        if not texto.endswith("}") and "}" in texto:
            texto = texto[: texto.rfind("}") + 1]
        data = json.loads(texto)

    if isinstance(data, list):
        return {"transacciones": data}

    if isinstance(data, dict):
        if "transacciones" in data and isinstance(data["transacciones"], list):
            return {"transacciones": data["transacciones"]}
        # Claves alternativas comunes
        for key in ["items", "filas", "movimientos", "rows", "data", "detalle"]:
            if key in data and isinstance(data[key], list):
                return {"transacciones": data[key]}
        # Puede ser un único registro
        return {"transacciones": [data]}

    # Si llega aquí, devolver vacío para forzar manejo aguas arriba
    return {"transacciones": []}


def _limpiar_valor_monetario(valor: object) -> float:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return 0.0

    s = str(valor).strip()
    if not s:
        return 0.0

    # Manejar negativos estilo contable (1) y signo -
    negativo_parentesis = s.startswith("(") and s.endswith(")")
    s = s.replace("(", "").replace(")", "")

    # Quitar símbolos de moneda, letras y espacios
    s = re.sub(r"[A-Za-z$€¢£¥₱₿\s]", "", s)

    # Contar separadores
    num_puntos = s.count(".")
    num_comas = s.count(",")

    if num_puntos > 0 and num_comas > 0:
        # Hay ambos, asumir que el separador más a la derecha es decimal
        last_dot = s.rfind(".")
        last_comma = s.rfind(",")
        if last_dot > last_comma:
            decimal_sep, thousands_sep = ".", ","
        else:
            decimal_sep, thousands_sep = ",", "."
        s = s.replace(thousands_sep, "")
        s = s.replace(decimal_sep, ".")
    elif num_comas > 0:
        # Solo comas presentes: para COP, tratar coma como miles salvo que sea caso claro decimal
        last = s.rfind(",")
        digits_after = len(re.sub(r"[^0-9]", "", s[last + 1 :]))
        digits_before = len(re.sub(r"[^0-9]", "", s[:last]))
        if digits_after == 3 and digits_before >= 1:
            # 1.234 o 12,345 → miles
            s = s.replace(",", "")
        elif re.search(r"^\d{1,3}(,\d{3})+(,\d{2})?$", s):
            # Agrupaciones de miles repetidas
            s = s.replace(",", "")
        else:
            # Caso decimal (p.ej. 40,50)
            s = s.replace(",", ".")
    elif num_puntos > 0:
        # Solo puntos presentes
        last = s.rfind(".")
        digits_after = len(re.sub(r"[^0-9]", "", s[last + 1 :]))
        digits_before = len(re.sub(r"[^0-9]", "", s[:last]))
        if digits_after == 3 and digits_before >= 1:
            # 40.000 → miles
            s = s.replace(".", "")
        elif re.search(r"^\d{1,3}(\.\d{3})+(\.\d{2})?$", s):
            s = s.replace(".", "")
        else:
            # Caso decimal (p.ej. 40.50)
            # Mantener el punto como decimal
            pass

    # Limpiar cualquier resto
    s = re.sub(r"[^0-9\.-]", "", s)

    try:
        numero = float(s)
    except Exception:
        numero = 0.0

    if negativo_parentesis:
        numero = -abs(numero)
    return numero


@dataclass
class ProcesadorGemini:
    api_key: str
    password: str
    carpeta: str
    log_callback: Optional[LogCallback] = None
    progress_callback: Optional[ProgresoCallback] = None
    modelo: str = "gemini-2.0-flash"
    max_reintentos: int = 3
    espera_inicial: float = 1.5

    _model: Optional[genai.GenerativeModel] = field(init=False, default=None)
    _log: LogCallback = field(init=False)

    def __post_init__(self) -> None:
        self.carpeta = str(self.carpeta)
        self._carpeta_path = Path(self.carpeta)
        self._log = self.log_callback if self.log_callback else lambda mensaje: logger.info(mensaje)

    # ------------------------------------------------------------------
    # Registro seguro
    # ------------------------------------------------------------------
    def _emitir(self, mensaje: str, nivel: int = logging.INFO) -> None:
        logger.log(nivel, mensaje)
        self._log(mensaje)

    # ------------------------------------------------------------------
    # Interacción con Gemini
    # ------------------------------------------------------------------
    def configurar_gemini(self) -> None:
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(
            model_name=self.modelo,
            safety_settings={"HARASSMENT": "block_none", "HATE": "block_none"},
            generation_config={"temperature": 0.0},
        )
        self._emitir("✅ Gemini configurado correctamente")

    def _invocar_modelo(self, contenido: Iterable[object]) -> str:
        if self._model is None:
            raise RuntimeError("El modelo de Gemini no ha sido configurado")

        for intento in range(1, self.max_reintentos + 1):
            try:
                respuesta = self._model.generate_content(list(contenido))
                return respuesta.text
            except Exception as exc:  # pragma: no-cover - depende de la API
                espera = self.espera_inicial * intento
                self._emitir(f"    ⚠️ Reintento {intento}/{self.max_reintentos}: {exc}")
                time.sleep(min(espera, 10))

        raise RuntimeError("Se agotaron los intentos de comunicación con Gemini")

    def _progreso(self, porcentaje: float, mensaje: str = "") -> None:
        try:
            if self.progress_callback is not None:
                self.progress_callback(float(max(0.0, min(100.0, porcentaje))), mensaje)
        except Exception:
            # El progreso no debe romper el flujo si falla la UI
            pass

    # ------------------------------------------------------------------
    # Procesamiento de PDFs
    # ------------------------------------------------------------------
    def desbloquear_pdf(self, pdf_path: Path) -> Optional[Path]:
        try:
            temporal = pdf_path.with_suffix(".temp.pdf")
            with Pdf.open(pdf_path, password=self.password) as pdf:
                pdf.save(temporal)
            return temporal
        except Exception as exc:
            self._emitir(f"  ✗ Error desbloqueando: {exc}", logging.ERROR)
            return None

    def pdf_a_imagenes(self, pdf_path: Path) -> Optional[List[Image.Image]]:
        try:
            documento = fitz.open(pdf_path)
            imagenes = []
            for pagina in documento:
                pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                imagenes.append(img)
            documento.close()
            return imagenes
        except Exception as exc:
            self._emitir(f"  ✗ Error convirtiendo PDF a imágenes: {exc}", logging.ERROR)
            return None

    def extraer_por_pagina(self, imagenes: List[Image.Image], banco: str) -> Optional[pd.DataFrame]:
        prompt = _PROMPTS.get(banco, _PROMPTS["bancolombia"])
        registros: List[Dict[str, str]] = []

        for indice, imagen in enumerate(imagenes, start=1):
            try:
                self._emitir(f"      • Procesando página {indice}/{len(imagenes)}")
                respuesta = self._invocar_modelo([prompt, imagen])
                datos = _limpiar_salida_json(respuesta)
                registros.extend(datos.get("transacciones", []))
                self._emitir(f"        ✓ {len(datos.get('transacciones', []))} transacciones")
            except Exception as exc:
                self._emitir(f"        ✗ No se pudo procesar la página {indice}: {exc}", logging.WARNING)

        if registros:
            return pd.DataFrame(registros)
        return None

    def extraer_transacciones(self, imagenes: List[Image.Image], nombre_archivo: str) -> Optional[pd.DataFrame]:
        banco = _normalizar_banco(nombre_archivo)

        if len(imagenes) > 3 and banco == "bancolombia":
            self._emitir("    📑 PDF extenso, procesamiento página por página")
            return self.extraer_por_pagina(imagenes, banco)

        prompt = _PROMPTS.get(banco, _PROMPTS["bancolombia"])

        try:
            self._emitir(f"    📤 Analizando {len(imagenes)} página(s) con modelo {self.modelo}")
            contenido = [prompt] + imagenes
            respuesta = self._invocar_modelo(contenido)
            datos = _limpiar_salida_json(respuesta)
            transacciones = datos.get("transacciones", [])
            if not transacciones:
                return None
            self._emitir(f"    ✅ {len(transacciones)} transacciones extraídas")
            return pd.DataFrame(transacciones)
        except Exception as exc:
            self._emitir(f"    ❌ Error analizando el PDF: {exc}", logging.ERROR)
            return None

    # ------------------------------------------------------------------
    # Normalización de resultados
    # ------------------------------------------------------------------
    def limpiar_valores_monetarios(self, df: pd.DataFrame) -> pd.DataFrame:
        columnas_monetarias = [
            columna
            for columna in df.columns
            if any(palabra in columna.lower() for palabra in ["valor", "saldo", "pagar", "capital", "interes", "restante"])
        ]

        for columna in columnas_monetarias:
            df[columna] = df[columna].apply(_limpiar_valor_monetario)

        return df

    def _normalizar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(col).strip() for col in df.columns]
        df = df.drop_duplicates().reset_index(drop=True)
        return self.limpiar_valores_monetarios(df)

    # ------------------------------------------------------------------
    # Clasificación IA de gastos
    # ------------------------------------------------------------------
    def _preparar_registros_clasificacion(self, df: pd.DataFrame) -> List[Dict[str, object]]:
        registros: List[Dict[str, object]] = []
        columnas_monto_preferidas = [
            "valor",
            "valor_transaccion",
            "total_pagar",
            "capital_facturado",
            "valor_del_mes",
            "saldo",
            "interes_mes",
            "restante",
        ]

        columnas_disponibles = [c for c in columnas_monto_preferidas if c in df.columns]
        columna_monto = columnas_disponibles[0] if columnas_disponibles else None

        for idx, fila in df.iterrows():
            registro: Dict[str, object] = {"idx": int(idx)}
            # Campos textuales informativos
            if "descripcion" in df.columns:
                registro["descripcion"] = str(fila.get("descripcion", ""))
            if "sucursal" in df.columns:
                registro["sucursal"] = str(fila.get("sucursal", ""))
            if "dcto" in df.columns:
                registro["dcto"] = str(fila.get("dcto", ""))
            if "tarjeta" in df.columns:
                registro["tarjeta"] = str(fila.get("tarjeta", ""))
            if "fecha" in df.columns:
                registro["fecha"] = str(fila.get("fecha", ""))

            # Monto numérico si existe
            if columna_monto is not None:
                try:
                    registro["monto"] = float(fila.get(columna_monto))
                except Exception:
                    registro["monto"] = 0.0

            registros.append(registro)

        return registros

    def clasificar_gastos(self, df: pd.DataFrame, categorias: Optional[List[str]] = None) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        categorias = categorias or _CATEGORIAS_GASTO

        try:
            registros = self._preparar_registros_clasificacion(df)
            instrucciones = (
                "Clasifica cada transacción en exactamente una de estas categorías: "
                + ", ".join(categorias)
                + ".\n"
                "Responde únicamente un JSON válido con el formato: "
                "{\"clasificaciones\":[{\"idx\":0,\"categoria\":\"...\"}]}\n"
                "Usa exclusivamente los nombres de categoría dados, sin crear nuevas."
            )

            contenido = [
                instrucciones,
                json.dumps({"transacciones": registros}, ensure_ascii=False),
            ]

            self._emitir("  🧠 Clasificando gastos con IA…")
            respuesta = self._invocar_modelo(contenido)

            # Normalizar posibles bloques con ```
            texto = respuesta.strip()
            if texto.startswith("```"):
                partes = texto.split("```")
                if len(partes) >= 2:
                    cuerpo = partes[1]
                    if cuerpo.lstrip().startswith("json"):
                        cuerpo = cuerpo.lstrip()[4:]
                    texto = cuerpo.strip()

            datos = json.loads(texto)
            clasificaciones = datos.get("clasificaciones", [])
            mapa_idx_categoria = {int(item.get("idx")): str(item.get("categoria", "")) for item in clasificaciones}

            df = df.copy()
            df["categoria"] = df.index.map(lambda i: mapa_idx_categoria.get(int(i), categorias[-1]))

            # Resumen por categoría
            try:
                resumen = df["categoria"].value_counts().to_dict()
                resumen_str = ", ".join([f"{k}: {v}" for k, v in resumen.items()])
                self._emitir(f"  ✓ Clasificación aplicada ({resumen_str})")
            except Exception:
                pass

            return df
        except Exception as exc:
            # Fallback: asignar categoría por defecto si algo falla
            self._emitir(f"  ⚠️ No se pudo clasificar con IA: {exc}")
            df = df.copy()
            if "categoria" not in df.columns:
                df["categoria"] = categorias[-1]
            return df

    # ------------------------------------------------------------------
    # Flujo principal
    # ------------------------------------------------------------------
    def procesar(self) -> Optional[Path]:
        try:
            self._emitir("=" * 60)
            self._emitir("🤖 INICIANDO PROCESAMIENTO CON GEMINI AI")
            self._emitir("=" * 60)
            self._progreso(0.0, "Iniciando…")

            if not self._carpeta_path.exists():
                raise FileNotFoundError(f"La carpeta {self._carpeta_path} no existe")

            self.configurar_gemini()

            pdfs = sorted([p for p in self._carpeta_path.glob("*.pdf") if not p.name.endswith(".temp.pdf")])
            if not pdfs:
                self._emitir("❌ No se encontraron PDFs en la carpeta indicada", logging.WARNING)
                return None

            self._emitir(f"\n📄 PDFs encontrados: {len(pdfs)}")
            for pdf in pdfs:
                self._emitir(f"   • {pdf.name}")

            excel_path = self._carpeta_path / "Extractos_Consolidados.xlsx"
            resultados: Dict[str, pd.DataFrame] = {}
            num_pdfs = len(pdfs)
            procesados = 0

            for pdf_path in pdfs:
                self._emitir("\n" + "━" * 60)
                self._emitir(f"📄 {pdf_path.name}")
                self._emitir("━" * 60)

                self._emitir("  🔓 Desbloqueando PDF protegido…")
                temp_pdf = self.desbloquear_pdf(pdf_path)
                if not temp_pdf or not temp_pdf.exists():
                    self._emitir("  ❌ No se pudo desbloquear el archivo", logging.ERROR)
                    procesados += 1
                    self._progreso((procesados / num_pdfs) * 100.0, f"{procesados}/{num_pdfs} - {pdf_path.name}")
                    continue

                self._emitir("  🖼️ Convirtiendo páginas a imágenes")
                imagenes = self.pdf_a_imagenes(temp_pdf)
                if not imagenes:
                    self._emitir("  ❌ Error durante la conversión a imágenes", logging.ERROR)
                    temp_pdf.unlink(missing_ok=True)
                    procesados += 1
                    self._progreso((procesados / num_pdfs) * 100.0, f"{procesados}/{num_pdfs} - {pdf_path.name}")
                    continue
                self._emitir(f"  ✓ {len(imagenes)} página(s) convertidas")

                self._emitir("  🤖 Analizando con Gemini…")
                df = self.extraer_transacciones(imagenes, pdf_path.stem)
                if df is None or df.empty:
                    self._emitir("  ❌ No se extrajeron datos útiles", logging.WARNING)
                    temp_pdf.unlink(missing_ok=True)
                    procesados += 1
                    self._progreso((procesados / num_pdfs) * 100.0, f"{procesados}/{num_pdfs} - {pdf_path.name}")
                    continue

                df = self._normalizar_dataframe(df)
                # Clasificación de gastos con IA (4 categorías propuestas)
                df = self.clasificar_gastos(df, categorias=_CATEGORIAS_GASTO)

                # Generar nombre de hoja único (límite Excel 31 caracteres)
                base = pdf_path.stem
                existente = set(resultados.keys())
                nombre_hoja = base[:31]
                if nombre_hoja in existente:
                    sufijo = 1
                    while True:
                        etiqueta = f"-{sufijo}"
                        candidato = (base[: (31 - len(etiqueta))] + etiqueta)[:31]
                        if candidato not in existente:
                            nombre_hoja = candidato
                            break
                        sufijo += 1
                resultados[nombre_hoja] = df

                self._emitir("\n  ✅ EXTRACCIÓN COMPLETA")
                self._emitir(f"     • Hoja: {nombre_hoja}")
                self._emitir(f"     • Filas: {len(df)}")
                self._emitir(f"     • Columnas: {len(df.columns)}")

                temp_pdf.unlink(missing_ok=True)

                # Avance por PDF completado
                procesados += 1
                self._progreso((procesados / num_pdfs) * 100.0, f"{procesados}/{num_pdfs} - {pdf_path.name}")

            if not resultados:
                self._emitir("\n❌ No se lograron extraer movimientos de los PDFs proporcionados", logging.WARNING)
                return None

            if excel_path.exists():
                respaldo = excel_path.with_suffix(".bak")
                excel_path.replace(respaldo)
                self._emitir(f"ℹ️ Copia de seguridad creada: {respaldo.name}")

            self._emitir("\n" + "=" * 60)
            self._emitir("💾 GENERANDO ARCHIVO EXCEL")
            self._emitir("=" * 60)

            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                for nombre_hoja, df in resultados.items():
                    df.to_excel(writer, sheet_name=nombre_hoja, index=False)
                    self._emitir(f"✓ Hoja '{nombre_hoja}' guardada ({len(df)} transacciones)")

            self._emitir(f"\n🎯 Archivo final: {excel_path}")
            self._progreso(100.0, "Completado")
            return excel_path
        except Exception as exc:
            self._emitir(f"\n❌ Error general durante el procesamiento: {exc}", logging.ERROR)
            logger.exception("Fallo inesperado en el procesamiento de extractos")
            return None


