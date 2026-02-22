from app.extractors.factura_borcelle import FacturaBorcelleExtractor

EXTRACTORS = [
    FacturaBorcelleExtractor(),
]

def run_extraction(texto: str) -> dict:
    for extractor in EXTRACTORS:
        if extractor.match(texto):
            data = extractor.extract(texto)
            data["modelo"] = extractor.__class__.__name__
            return data

    return {"modelo": "unknown", "error": "No matching extractor found"}
