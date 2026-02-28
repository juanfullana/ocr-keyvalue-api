from app.extractors.factura_borcelle import FacturaBorcelleExtractor
from app.extractors.generic_factura import GenericFacturaExtractor

EXTRACTORS = [
    FacturaBorcelleExtractor(),
]

def aplicar_validaciones(data: dict, modelo: str) -> dict:

    validaciones = {
        "numero_factura_detectado": bool(data.get("numero_factura")),
        "fecha_detectada": bool(data.get("fecha_emision")),
        "total_detectado": "total" in data.get("totales", {})
    }

    campos_ok = sum(validaciones.values())
    confidence = round(campos_ok / len(validaciones), 2)

    data["validaciones"] = validaciones
    data["confidence"] = confidence
    data["modelo"] = modelo

    return data


def run_extraction(texto: str) -> dict:

    # 1️⃣ Intentar extractores específicos
    for extractor in EXTRACTORS:
        if extractor.match(texto):
            data = extractor.extract(texto)
            return aplicar_validaciones(data, extractor.__class__.__name__)

    # 2️⃣ Fallback genérico
    generic = GenericFacturaExtractor()
    data = generic.extract(texto)

    return aplicar_validaciones(data, "GenericFacturaExtractor")