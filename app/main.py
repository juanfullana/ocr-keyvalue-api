from fastapi import FastAPI, UploadFile, File
from app.ocr_service import procesar_imagen

app = FastAPI(title="OCR KeyValue API")

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/procesar")
async def procesar(file: UploadFile = File(...)):
    resultado = await procesar_imagen(file)
    return resultado