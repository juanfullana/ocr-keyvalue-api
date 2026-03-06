import easyocr
import shutil
import os
import time
import numpy as np
import cv2
import pdfplumber
import uuid

from datetime import datetime
from pdf2image import convert_from_path

from app.text_rebuilder import reconstruir_lineas
from app.text_cleaner import limpiar_texto_ocr
from app.document_classifier import clasificar_documento
from app.extractor_engine import run_extraction
from app.ocr_visualizer import dibujar_cajas


# Inicialización OCR (una sola vez)
reader = easyocr.Reader(['es'], gpu=False)


async def procesar_imagen(file):

    inicio = time.time()

    ruta_temp = f"temp_{file.filename}"

    try:

        # Guardar archivo temporal
        with open(ruta_temp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        texto = ""
        resultados = None
        imagen_debug = None

        # -----------------------------------
        # PDF
        # -----------------------------------
        if ruta_temp.lower().endswith(".pdf"):

            texto_pdf = ""

            try:

                with pdfplumber.open(ruta_temp) as pdf:

                    for pagina in pdf.pages:

                        contenido = pagina.extract_text()

                        if contenido:
                            texto_pdf += contenido + "\n"

            except:
                texto_pdf = ""

            # PDF con texto digital
            if texto_pdf.strip():

                texto = texto_pdf

            # PDF escaneado → OCR
            else:

                imagenes = convert_from_path(ruta_temp)

                for img in imagenes:

                    imagen_np = np.array(img)

                    resultados = reader.readtext(imagen_np)

                    texto += reconstruir_lineas(resultados) + "\n"

                    imagen_debug = dibujar_cajas(imagen_np, resultados)

        # -----------------------------------
        # Imagen
        # -----------------------------------
        else:

            imagen = cv2.imread(ruta_temp)

            resultados = reader.readtext(ruta_temp)

            texto = reconstruir_lineas(resultados)

            imagen_debug = dibujar_cajas(imagen, resultados)

        # -----------------------------------
        # Limpieza OCR
        # -----------------------------------
        texto = limpiar_texto_ocr(texto)

        # -----------------------------------
        # Clasificar documento
        # -----------------------------------
        tipo_documento = clasificar_documento(texto)

        # -----------------------------------
        # Extracción de datos
        # -----------------------------------
        datos = run_extraction(texto)

        # -----------------------------------
        # Guardar imagen debug
        # -----------------------------------
        imagen_url = None

        if imagen_debug is not None:

            debug_filename = f"{uuid.uuid4()}.png"

            debug_path = os.path.join("debug", debug_filename)

            cv2.imwrite(debug_path, imagen_debug)

            imagen_url = f"/debug/{debug_filename}"

        # -----------------------------------
        # Tiempo procesamiento
        # -----------------------------------
        fin = time.time()

        tiempo_ms = int((fin - inicio) * 1000)

        # -----------------------------------
        # Sugerencia expediente
        # -----------------------------------
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

            "imagen_debug": imagen_url,

            "texto_detectado": texto,

            "datos_extraidos": datos,

            "sugerencia_expediente": sugerencia
        }

    finally:

        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)