from fastapi import FastAPI, UploadFile, File
from app.ocr_service import procesar_imagen
from typing import List
from fastapi import UploadFile, File

app = FastAPI(title="OCR KeyValue API")

@app.get("/")
def health():
    return {
        "api": "OCR Ingreso Expedientes",
        "version": "1.0",
        "estado": "operativa"
    }

@app.post("/procesar")
async def procesar(file: UploadFile = File(...)):
    resultado = await procesar_imagen(file)
    return resultado

@app.post("/procesar-lote")
async def procesar_lote(files: List[UploadFile] = File(...)):
    resultados = []

    for file in files:
        try:
            resultado = await procesar_imagen(file)
            resultados.append({
                "archivo": file.filename,
                "estado": "ok",
                "datos": resultado
            })
        except Exception as e:
            resultados.append({
                "archivo": file.filename,
                "estado": "error",
                "mensaje": str(e)
            })

    return resultados