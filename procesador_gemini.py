"""
Módulo procesador de PDFs con Gemini AI
"""

from pathlib import Path
import pandas as pd
import google.generativeai as genai
from PIL import Image
import io
import fitz
import json
from pikepdf import Pdf
import re


class ProcesadorGemini:
    def __init__(self, api_key, password, carpeta, log_callback=None):
        self.api_key = api_key
        self.password = password
        self.carpeta = Path(carpeta)
        self.log = log_callback if log_callback else print
        self.model = None
        
    def configurar_gemini(self):
        """Configura Gemini AI"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.log("✅ Gemini 2.0 Flash configurado")
        
    def desbloquear_pdf(self, pdf_path):
        """Desbloquea un PDF con contraseña"""
        try:
            temp_pdf_path = pdf_path.with_suffix('.temp.pdf')
            with Pdf.open(pdf_path, password=self.password) as pdf:
                pdf.save(temp_pdf_path)
            return temp_pdf_path
        except Exception as e:
            self.log(f"  ✗ Error desbloqueando: {str(e)}")
            return None
    
    def pdf_a_imagenes(self, pdf_path):
        """Convierte PDF a imágenes"""
        try:
            doc = fitz.open(pdf_path)
            imagenes = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                imagenes.append(img)
            
            doc.close()
            return imagenes
        except Exception as e:
            self.log(f"  ✗ Error convirtiendo: {str(e)}")
            return None
    
    def extraer_por_pagina(self, imagenes, nombre_banco):
        """Extrae transacciones página por página"""
        
        prompt_base = """
Analiza esta página de un extracto bancario de Bancolombia y extrae SOLO las transacciones.

Busca la tabla de movimientos con estas columnas: FECHA, DESCRIPCIÓN, SUCURSAL, DCTO., VALOR, SALDO.

IMPORTANTE:
- Extrae TODAS las transacciones que veas
- No omitas ninguna fila
- Si ves información de resumen, ignórala
- Solo transacciones/movimientos

Formato JSON:
{
  "transacciones": [
    {
      "fecha": "fecha",
      "descripcion": "descripción completa",
      "sucursal": "sucursal",
      "dcto": "documento",
      "valor": "valor (con signo)",
      "saldo": "saldo"
    }
  ]
}

Responde SOLO con el JSON.
"""
        
        todas_transacciones = []
        
        for i, imagen in enumerate(imagenes, 1):
            try:
                self.log(f"      • Página {i}/{len(imagenes)}...")
                
                contenido = [prompt_base, imagen]
                response = self.model.generate_content(contenido)
                texto = response.text.strip()
                
                # Limpiar
                if texto.startswith("```"):
                    lineas = texto.split("```")
                    if len(lineas) >= 2:
                        texto = lineas[1]
                        if texto.startswith("json"):
                            texto = texto[4:]
                    texto = texto.strip()
                
                # Reparar JSON
                if not texto.endswith("}"):
                    ultimo = texto.rfind("}")
                    if ultimo > 0:
                        texto = texto[:ultimo+1] + "\n  ]\n}"
                
                datos = json.loads(texto)
                
                if "transacciones" in datos and datos["transacciones"]:
                    todas_transacciones.extend(datos["transacciones"])
                    self.log(f"        ✓ {len(datos['transacciones'])} transacciones")
            except Exception as e:
                self.log(f"        ✗ Error: {str(e)[:50]}")
                continue
        
        if todas_transacciones:
            df = pd.DataFrame(todas_transacciones)
            return df
        return None
    
    def extraer_transacciones(self, imagenes, nombre_banco):
        """Extrae transacciones de las imágenes"""
        
        # PDFs grandes: procesar página por página
        if len(imagenes) > 3 and ("CTA_AHORROS" in nombre_banco or "908096306" in nombre_banco):
            self.log("    📑 PDF grande, procesando página por página...")
            return self.extraer_por_pagina(imagenes, nombre_banco)
        
        # Prompts por banco
        prompts = {
            "Nu": """
Extrae las transacciones de Nu Bank en JSON.
Columnas: Fecha, Descripción, Valor, Cuotas, Valor del mes, Interés del mes, Total a pagar, Restante.
Ignora encabezados y publicidad.

Formato:
{"transacciones": [{"fecha":"","descripcion":"","valor":"","cuotas":"","valor_del_mes":"","interes_mes":"","total_pagar":"","restante":""}]}

Solo JSON, sin texto adicional.
""",
            "Rappi": """
Extrae transacciones de tarjeta Davivienda (Rappi) en JSON.
Busca "Detalle de transacciones" con columnas: Tarjeta, Fecha, Descripción, Valor transacción, Capital facturado, Cuotas, Capital pendiente, Tasa.

Formato:
{"transacciones": [{"tarjeta":"","fecha":"","descripcion":"","valor_transaccion":"","capital_facturado":"","cuotas":"","capital_pendiente":"","tasa_mv":"","tasa_ea":""}]}

Solo JSON.
""",
            "Bancolombia": """
Extrae movimientos de cuenta Bancolombia en JSON.
Columnas: FECHA, DESCRIPCIÓN, SUCURSAL, DCTO., VALOR, SALDO.

Formato:
{"transacciones": [{"fecha":"","descripcion":"","sucursal":"","dcto":"","valor":"","saldo":""}]}

Solo JSON.
"""
        }
        
        # Seleccionar prompt
        if "Nu" in nombre_banco:
            prompt = prompts["Nu"]
        elif "CREDIT_CARD" in nombre_banco:
            prompt = prompts["Rappi"]
        else:
            prompt = prompts["Bancolombia"]
        
        try:
            self.log(f"    📤 Enviando {len(imagenes)} página(s) a Gemini...")
            
            contenido = [prompt] + imagenes
            response = self.model.generate_content(contenido)
            texto = response.text.strip()
            
            # Limpiar
            if texto.startswith("```"):
                lineas = texto.split("```")
                if len(lineas) >= 2:
                    texto = lineas[1]
                    if texto.startswith("json"):
                        texto = texto[4:]
                texto = texto.strip()
            
            if not texto.endswith("}"):
                ultimo = texto.rfind("}")
                if ultimo > 0:
                    texto = texto[:ultimo+1] + "\n  ]\n}"
            
            datos = json.loads(texto)
            
            if "transacciones" in datos and datos["transacciones"]:
                self.log(f"    ✅ {len(datos['transacciones'])} transacciones extraídas")
                df = pd.DataFrame(datos["transacciones"])
                return df
                
        except Exception as e:
            self.log(f"    ❌ Error: {str(e)}")
        
        return None
    
    def limpiar_valor_monetario(self, valor):
        """Convierte texto monetario a número"""
        if pd.isna(valor) or valor in ['nan', 'None', '']:
            return 0.0
        
        valor_str = str(valor)
        valor_str = valor_str.replace('$', '').replace('€', '').replace('COP', '').strip()
        valor_str = valor_str.replace('.', '')
        valor_str = valor_str.replace(',', '.')
        valor_str = re.sub(r'[a-zA-Z].*', '', valor_str).strip()
        valor_str = valor_str.replace('%', '')
        
        try:
            return float(valor_str)
        except:
            return 0.0
    
    def limpiar_valores_monetarios(self, df):
        """Limpia columnas monetarias del DataFrame"""
        columnas_monetarias = [col for col in df.columns if 
                               'valor' in col.lower() or 'saldo' in col.lower() or 
                               'pagar' in col.lower() or 'capital' in col.lower() or 
                               'interes' in col.lower() or 'restante' in col.lower()]
        
        for col in columnas_monetarias:
            df[col] = df[col].apply(self.limpiar_valor_monetario)
        
        return df
    
    def procesar(self):
        """Procesa todos los PDFs"""
        try:
            self.log("="*60)
            self.log("🤖 INICIANDO PROCESAMIENTO CON GEMINI AI")
            self.log("="*60)
            
            # Configurar Gemini
            self.configurar_gemini()
            
            # Buscar PDFs
            pdfs = [p for p in self.carpeta.glob("*.pdf") if not p.name.endswith('.temp.pdf')]
            
            if not pdfs:
                self.log("\n❌ No se encontraron PDFs")
                return None
            
            self.log(f"\n📄 PDFs encontrados: {len(pdfs)}")
            for pdf in pdfs:
                self.log(f"   • {pdf.name}")
            
            excel_path = self.carpeta / "Extractos_Consolidados.xlsx"
            resultados = {}
            
            # Procesar cada PDF
            for pdf_path in pdfs:
                self.log(f"\n{'━'*60}")
                self.log(f"📄 {pdf_path.name}")
                self.log('━'*60)
                
                # Desbloquear
                self.log("  🔓 Desbloqueando...")
                temp_pdf = self.desbloquear_pdf(pdf_path)
                
                if not temp_pdf or not temp_pdf.exists():
                    self.log("  ❌ No se pudo desbloquear")
                    continue
                
                self.log("  ✓ Desbloqueado")
                
                # Convertir a imágenes
                self.log("  🖼️  Convirtiendo a imágenes...")
                imagenes = self.pdf_a_imagenes(temp_pdf)
                
                if not imagenes:
                    self.log("  ❌ No se pudo convertir")
                    temp_pdf.unlink()
                    continue
                
                self.log(f"  ✓ {len(imagenes)} página(s) convertidas")
                
                # Extraer con Gemini
                self.log("  🤖 Analizando con Gemini...")
                df = self.extraer_transacciones(imagenes, pdf_path.stem)
                
                if df is not None and not df.empty:
                    # Limpiar valores
                    df = self.limpiar_valores_monetarios(df)
                    
                    nombre_hoja = pdf_path.stem[:31]
                    resultados[nombre_hoja] = df
                    
                    self.log(f"\n  ✅ ÉXITO:")
                    self.log(f"     • Hoja: '{nombre_hoja}'")
                    self.log(f"     • Transacciones: {len(df)}")
                    self.log(f"     • Columnas: {len(df.columns)}")
                else:
                    self.log("  ❌ No se extrajeron datos")
                
                # Limpiar temporal
                if temp_pdf.exists():
                    temp_pdf.unlink()
            
            # Guardar Excel
            if resultados:
                self.log(f"\n{'='*60}")
                self.log("💾 GUARDANDO EXCEL")
                self.log("="*60)
                
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    for nombre_hoja, df in resultados.items():
                        df.to_excel(writer, sheet_name=nombre_hoja, index=False)
                        self.log(f"✓ Hoja '{nombre_hoja}' guardada ({len(df)} transacciones)")
                
                return excel_path
            else:
                self.log("\n❌ No se extrajeron datos")
                return None
                
        except Exception as e:
            self.log(f"\n❌ Error general: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return None

