import re
from .base_extractor import BaseExtractor


class GenericFacturaExtractor(BaseExtractor):

    def limpiar_numero(self, valor: str) -> float:
        """
        Convierte números europeos tipo 199,65 o 1.234,56 a float.
        """
        valor = valor.replace(".", "").replace(",", ".").replace("€", "").strip()
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

        texto_upper = texto.upper()

        # -------------------------
        # NÚMERO DE FACTURA
        # -------------------------

        # Caso 1: tabla tipo
        # FACTURA PEDIDO FECHA
        # 01234   01234  28/07/2030
        tabla_match = re.search(
            r"FACTURA\s+PEDIDO\s+FECHA.*?\n?(\d{3,})\s+\d{3,}\s+\d{2}/\d{2}/\d{4}",
            texto,
            re.S
        )

        if tabla_match:
            datos["numero_factura"] = tabla_match.group(1)

        # Caso 2: FACTURA N° 12345
        if not datos["numero_factura"]:

            numero_match = re.search(
                r"FACTURA\s*(?:N[°º]|NRO|NUMERO)?\s*[:\-]?\s*(\d{3,})",
                texto,
                re.I
            )

            if numero_match:
                datos["numero_factura"] = numero_match.group(1)

        # Caso 2: estructura tabla
        # FACTURA PEDIDO FECHA
        # 01234   01234  28/07/2030

        if not datos["numero_factura"]:

            tabla_match = re.search(
                r"FACTURA\s+PEDIDO\s+FECHA.*?\n?(\d{3,})\s+\d{3,}\s+\d{2}/\d{2}/\d{4}",
                texto_upper,
                re.S
            )

            if tabla_match:
                datos["numero_factura"] = tabla_match.group(1)

        # -------------------------
        # FECHA
        # -------------------------

        fecha_match = re.search(r"\b\d{2}[./]\d{2}[./]\d{4}\b", texto)

        if fecha_match:
            datos["fecha_emision"] = fecha_match.group()

        # -------------------------
        # TOTAL FINAL
        # Busca TOTAL + número o número seguido de €
        # -------------------------

        total_matches = re.findall(
            r"TOTAL.*?(\d+[.,]?\d*)\s*€?",
            texto_upper,
            re.S
        )

        if total_matches:
            try:
                total_limpio = self.limpiar_numero(total_matches[-1])
                datos["totales"]["total"] = total_limpio
            except:
                pass

        # fallback: detectar número seguido de €
        if "total" not in datos["totales"]:

            euro_match = re.findall(
                r"(\d+[.,]?\d*)\s*€",
                texto
            )

            if euro_match:
                try:
                    datos["totales"]["total"] = self.limpiar_numero(euro_match[-1])
                except:
                    pass

        # -------------------------
        # SUBTOTAL
        # -------------------------

        subtotal_match = re.search(
            r"SUBTOTAL\s*[:\-]?\s*(\d+[.,]\d+)",
            texto_upper
        )

        if subtotal_match:
            try:
                subtotal_limpio = self.limpiar_numero(subtotal_match.group(1))
                datos["totales"]["subtotal"] = subtotal_limpio
            except:
                pass

        # -------------------------
        # IVA
        # -------------------------

        iva_match = re.search(
            r"IVA.*?(\d+[.,]\d+)",
            texto_upper
        )

        if iva_match:
            try:
                iva_limpio = self.limpiar_numero(iva_match.group(1))
                datos["totales"]["iva"] = iva_limpio
            except:
                pass

        return datos