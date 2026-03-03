import easyocr
import shutil
import os
import time
from datetime import datetime

from app.extractor_engine import run_extraction


# Inicialización del OCR (una sola vez)
reader = easyocr.Reader(['es'], gpu=False)


async def procesar_imagen(file):

    inicio = time.time()  # ⏱ Inicio medición

    ruta_temp = f"temp_{file.filename}"

    try:
        # Guardar archivo temporal
        with open(ruta_temp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ejecutar OCR
        resultados = reader.readtext(ruta_temp)

        # Ordenar resultados por posición (fila, columna)
        resultados_ordenados = sorted(
            resultados,
            key=lambda r: (r[0][0][1], r[0][0][0])
        )

        texto = "\n".join([r[1] for r in resultados_ordenados])

        # Ejecutar extracción
        datos = run_extraction(texto)

        # ⏱ Fin medición
        fin = time.time()
        tiempo_ms = int((fin - inicio) * 1000)

        # Sugerencia para expediente (neutral)
        sugerencia = {
            "proveedor_cuit": datos.get("cuit", "no_detectado"),
            "numero_factura": datos.get("numero_factura"),
            "fecha": datos.get("fecha_emision"),
            "importe": datos.get("totales", {}).get("total")
        }

        return {
            "procesado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tiempo_procesamiento_ms": tiempo_ms,
            "texto_detectado": texto,
            "datos_extraidos": datos,
            "sugerencia_expediente": sugerencia
        }

    finally:
        # Asegura que el archivo temporal siempre se borre
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)