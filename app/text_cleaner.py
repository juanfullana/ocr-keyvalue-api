import re
import unicodedata


def limpiar_texto_ocr(texto: str) -> str:

    # Normalizar acentos
    texto = unicodedata.normalize("NFKD", texto)

    # Pasar a mayúsculas
    texto = texto.upper()

    # Reemplazos comunes de OCR
    reemplazos = {
        "FACTURQ": "FACTURA",
        "FACTUR4": "FACTURA",
        "N?": "N°",
        "NO ": "N° ",
        "CP;": "CP:",
        "IBAN:": "IBAN ",
        "|": "",
        "{": "",
        "}": "",
    }

    for k, v in reemplazos.items():
        texto = texto.replace(k, v)

    # Limpiar caracteres raros
    texto = re.sub(r"[^A-Z0-9€.,:/°\-\n ]", "", texto)

    # Normalizar espacios
    texto = re.sub(r"\s+", " ", texto)

    # Reinsertar saltos de línea útiles
    texto = texto.replace(" TOTAL ", "\nTOTAL ")
    texto = texto.replace(" IVA ", "\nIVA ")

    return texto.strip()