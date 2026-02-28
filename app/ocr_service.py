import easyocr
import shutil
import os
from app.extractor_engine import run_extraction  

reader = easyocr.Reader(['es'], gpu=False)

async def procesar_imagen(file):
    ruta_temp = f"temp_{file.filename}"

    with open(ruta_temp, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resultados = reader.readtext(ruta_temp)

    resultados_ordenados = sorted(
        resultados,
        key=lambda r: (r[0][0][1], r[0][0][0])
    )

    texto = "\n".join([r[1] for r in resultados_ordenados])  

    datos = run_extraction(texto)  
    os.remove(ruta_temp)

    sugerencia = {
    "proveedor_cuit": datos.get("cuit", "no_detectado"),
    "numero_factura": datos.get("numero_factura"),
    "fecha": datos.get("fecha_emision"),
    "importe": datos.get("totales", {}).get("total"),
    "estado_inicial": "BORRADOR_AUTOGENERADO"
}

    return {
    "texto_detectado": texto,
    "datos_extraidos": datos,
    "sugerencia_expediente": sugerencia
}
