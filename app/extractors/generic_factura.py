import re
from .base_extractor import BaseExtractor


class GenericFacturaExtractor(BaseExtractor):

    def limpiar_numero(self, valor: str) -> float:
        """
        Convierte números europeos tipo 199,65 o 1.234,56 a float.
        """
        valor = valor.replace(".", "").replace(",", ".")
        return float(valor)

    def match(self, texto: str) -> bool:
        """
        Extractor genérico: se activa si detecta la palabra FACTURA.
        """
        return "FACTURA" in texto.upper()

    def extract(self, texto: str) -> dict:

        datos = {
            "numero_factura": None,
            "fecha_emision": None,
            "items": [],
            "totales": {}
        }

        # -------------------------
        # NÚMERO DE FACTURA
        # -------------------------
        numero_match = re.search(
            r"(N[°º\?]?\s*DE\s*FACTURA|FACTURA\s*N[°º]?)[^\n]*\n?\s*([A-Z0-9\-]+)",
            texto,
            re.I
        )

        if numero_match:
            datos["numero_factura"] = numero_match.group(2).strip()

        # -------------------------
        # FECHA (formato europeo)
        # -------------------------
        fecha_match = re.search(r"\b\d{2}[./]\d{2}[./]\d{4}\b", texto)
        if fecha_match:
            datos["fecha_emision"] = fecha_match.group()

        # -------------------------
        # TOTAL FINAL
        # Busca todas las ocurrencias de TOTAL + número
        # y se queda con la última
        # -------------------------
        total_matches = re.findall(
            r"TOTAL\s*[\n ]*(\d+[.,]\d+)",
            texto,
            re.I
        )

        if total_matches:
            try:
                total_limpio = self.limpiar_numero(total_matches[-1])
                datos["totales"]["total"] = total_limpio
            except:
                pass

        # -------------------------
        # SUBTOTAL (opcional)
        # -------------------------
        subtotal_match = re.search(
            r"SUBTOTAL\s*[\n ]*(\d+[.,]\d+)",
            texto,
            re.I
        )

        if subtotal_match:
            try:
                subtotal_limpio = self.limpiar_numero(subtotal_match.group(1))
                datos["totales"]["subtotal"] = subtotal_limpio
            except:
                pass

        # -------------------------
        # IVA (si aparece explícito)
        # -------------------------
        iva_match = re.search(
            r"IVA\s*.*?(\d+[.,]\d+)",
            texto,
            re.I
        )

        if iva_match:
            try:
                iva_limpio = self.limpiar_numero(iva_match.group(1))
                datos["totales"]["iva"] = iva_limpio
            except:
                pass

        return datos