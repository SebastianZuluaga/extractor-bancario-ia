"""API HTTP para procesar extractos con IA y devolver Excel consolidado.

Endpoints:
- GET /salud: Verificación básica
- POST /procesar: Recibe múltiples PDFs (multipart), opcionalmente contraseña
  y API Key de Gemini, y retorna el archivo Excel generado.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response, FileResponse

from fastapi.staticfiles import StaticFiles
from app.core.logger import setup_logger
from app.services.gemini_processor import GeminiProcessor


app = FastAPI(title="Extractor Bancario IA - API", version="1.0.0")

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

logger, _ = setup_logger("app.api")


def _guardar_archivos_temporales(archivos: List[UploadFile]) -> Path:
    carpeta_trabajo = Path(tempfile.mkdtemp(prefix="api-procesar-"))
    for archivo in archivos:
        nombre = Path(archivo.filename or "").name
        if not nombre.lower().endswith(".pdf"):
            # Aceptamos solo PDFs
            raise HTTPException(status_code=400, detail=f"Archivo no permitido: {nombre}")
        destino = carpeta_trabajo / nombre
        with destino.open("wb") as f:
            f.write(archivo.file.read())
    return carpeta_trabajo


@app.get("/")
def read_root():
    return FileResponse(static_dir / 'index.html')

@app.get("/salud")
def salud() -> dict:
    return {"status": "ok"}


@app.post("/procesar")
def procesar(
    files: List[UploadFile] = File(..., description="Uno o más PDFs"),
    password: Optional[str] = Form(None, description="Contraseña PDF si aplica"),
    gemini_api_key: Optional[str] = Form(None, description="API Key de Gemini si no se define en el servidor"),
):
    if not files:
        raise HTTPException(status_code=400, detail="Debes adjuntar al menos un PDF")

    api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Falta API Key de Gemini (env GEMINI_API_KEY o form gemini_api_key)")

    try:
        carpeta = _guardar_archivos_temporales(files)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error guardando archivos temporales")
        raise HTTPException(status_code=500, detail=f"Error guardando archivos: {exc}")

    contenido_excel: bytes = b""
    nombre_descarga = f"Extractos_Consolidados_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"

    try:
        logger.info("Procesando %d PDF(s) en %s", len(files), carpeta)
        procesador = GeminiProcessor(
            api_key=api_key,
            password=password or "",
            carpeta=str(carpeta),
            log_callback=lambda m: logger.info(m),
            progress_callback=lambda p, msg=None: None,
        )
        excel_path = procesador.procesar()
        if not excel_path or not Path(excel_path).exists():
            raise HTTPException(status_code=500, detail="No fue posible generar el Excel")

        with open(excel_path, "rb") as f:
            contenido_excel = f.read()

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Fallo durante el procesamiento de PDFs")
        raise HTTPException(status_code=500, detail=f"Error procesando PDFs: {exc}")
    finally:
        try:
            shutil.rmtree(carpeta, ignore_errors=True)
        except Exception:
            pass

    headers = {
        "Content-Disposition": f"attachment; filename={nombre_descarga}",
        "X-Processed-At": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return Response(
        content=contenido_excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@app.post("/api/analyze")
def analyze_pdfs(
    files: List[UploadFile] = File(...),
    password: Optional[str] = Form(None),
    gemini_api_key: Optional[str] = Form(None),
):
    api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Missing API Key")

    try:
        carpeta = _guardar_archivos_temporales(files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        procesador = GeminiProcessor(
            api_key=api_key,
            password=password or "",
            carpeta=str(carpeta)
        )
        
        # Process PDFs to get DataFrame
        # We need to modify procesador_gemini.py to allow returning the DF directly
        # For now, we'll assume a new method or modify the existing one
        # Let's assume we add a method `obtener_datos_consolidados`
        
        datos = procesador.obtener_datos_consolidados()
        
        return datos

    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8000)),
        reload=False,
    )


