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
    total_campos = len(validaciones)

    confidence = round(campos_ok / total_campos, 2)

    # Estado lógico de extracción
    if confidence == 1:
        estado_extraccion = "completo"
    elif confidence >= 0.6:
        estado_extraccion = "parcial"
    else:
        estado_extraccion = "incompleto"

    requiere_revision = confidence < 0.8

    # Clasificación de negocio
    if "Borcelle" in modelo:
        tipo_documento = "factura"
        plantilla_detectada = "proveedor_borcelle"
    else:
        tipo_documento = "factura"
        plantilla_detectada = "generica"

    data["clasificacion"] = {
        "tipo_documento": tipo_documento,
        "plantilla_detectada": plantilla_detectada,
        "confidence_clasificacion": confidence
    }

    data["validaciones"] = validaciones
    data["confidence"] = confidence
    data["estado_extraccion"] = estado_extraccion
    data["requiere_revision"] = requiere_revision
    data["modelo_tecnico"] = modelo

    return data


def run_extraction(texto: str) -> dict:

    # Intentar extractores específicos
    for extractor in EXTRACTORS:
        if extractor.match(texto):
            data = extractor.extract(texto)
            return aplicar_validaciones(data, extractor.__class__.__name__)

    # Fallback genérico
    generic = GenericFacturaExtractor()
    data = generic.extract(texto)

    return aplicar_validaciones(data, "GenericFacturaExtractor")