import easyocr
import shutil
import os
import time
import numpy as np
import pdfplumber
from datetime import datetime
from pdf2image import convert_from_path

from app.document_classifier import clasificar_documento
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

        texto = ""

        # 📄 Si es PDF
        if ruta_temp.lower().endswith(".pdf"):

            texto_pdf = ""

            # Intentar leer texto directo del PDF (MUCHO más rápido)
            try:
                with pdfplumber.open(ruta_temp) as pdf:
                    for pagina in pdf.pages:
                        contenido = pagina.extract_text()
                        if contenido:
                            texto_pdf += contenido + "\n"
            except:
                texto_pdf = ""

            # Si el PDF tiene texto digital → usarlo
            if texto_pdf.strip():
                texto = texto_pdf

            # Si no tiene texto → aplicar OCR
            else:

                imagenes = convert_from_path(ruta_temp)

                for img in imagenes:

                    resultados = reader.readtext(np.array(img))

                    resultados_ordenados = sorted(
                        resultados,
                        key=lambda r: (r[0][0][1], r[0][0][0])
                    )

                    texto += "\n".join([r[1] for r in resultados_ordenados]) + "\n"

        # 🖼 Si es imagen → OCR directo
        else:

            resultados = reader.readtext(ruta_temp)

            resultados_ordenados = sorted(
                resultados,
                key=lambda r: (r[0][0][1], r[0][0][0])
            )

            texto = "\n".join([r[1] for r in resultados_ordenados])

        # 🧠 Clasificar tipo de documento
        tipo_documento = clasificar_documento(texto)

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
            "tipo_documento": tipo_documento,
            "texto_detectado": texto,
            "datos_extraidos": datos,
            "sugerencia_expediente": sugerencia
        }

    finally:
        # Asegura que el archivo temporal siempre se borre
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)