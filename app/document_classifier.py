def clasificar_documento(texto: str):

    texto = texto.upper()

    reglas = {
        "factura": [
            "FACTURA",
            "IVA",
            "TOTAL",
            "N° DE FACTURA",
            "BASE IMPONIBLE"
        ],
        "recibo": [
            "RECIBO",
            "PAGADO",
            "IMPORTE RECIBIDO"
        ],
        "contrato": [
            "CONTRATO",
            "CLAUSULA",
            "PARTES"
        ],
        "expediente": [
            "EXPEDIENTE",
            "MUNICIPALIDAD",
            "SECRETARIA"
        ]
    }

    scores = {}

    for tipo, palabras in reglas.items():
        score = 0
        for palabra in palabras:
            if palabra in texto:
                score += 1
        scores[tipo] = score

    tipo_detectado = max(scores, key=scores.get)

    if scores[tipo_detectado] == 0:
        return "desconocido"

    return tipo_detectado