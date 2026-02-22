import re
from .base_extractor import BaseExtractor


class FacturaBorcelleExtractor(BaseExtractor):

    def limpiar_numero(self, valor: str) -> float:
        valor = valor.replace("€", "").replace(",", "").strip()
        return float(valor)

    def match(self, texto: str) -> bool:
        """
        Determina si el documento corresponde al modelo Borcelle.
        """
        return "borcelle" in texto.lower()

    def extract(self, texto: str) -> dict:

        datos = {
            "numero_factura": None,
            "fecha_emision": None,
            "emisor": {},
            "items": [],
            "totales": {}
        }

        # -------------------
        # Número y fecha
        # -------------------
        numero_match = re.search(r"\n(\d{5})\n\d{2}/\d{2}/\d{4}", texto)
        if numero_match:
            datos["numero_factura"] = numero_match.group(1)

        fecha_match = re.search(r"\d{2}/\d{2}/\d{4}", texto)
        if fecha_match:
            datos["fecha_emision"] = fecha_match.group()

        # -------------------
        # Emisor
        # -------------------
        emisor_match = re.search(r"EMITIDA POR:\n([^\n]+)\n([^\n]+)", texto)
        if emisor_match:
            datos["emisor"]["nombre"] = emisor_match.group(2)

        # -------------------
        # Tabla de productos
        # -------------------
        lineas = [l.strip() for l in texto.split("\n") if l.strip()]
        items = []

        i = 0
        while i < len(lineas):

            linea = lineas[i]

            # Detectar descripción (evitar líneas numéricas)
            if (
                not re.search(r"\d+€?", linea)
                and (
                    "Servicio" in linea
                    or "Optimizacion" in linea
                    or "Creacion" in linea
                )
            ):

                descripcion = linea
                cantidad = 1

                try:
                    precio = re.search(r"\d+", lineas[i + 1]).group()
                    iva = re.search(r"\d+", lineas[i + 2]).group()
                    total = re.search(r"\d+", lineas[i + 3]).group()

                    items.append({
                        "descripcion": descripcion,
                        "cantidad": cantidad,
                        "precio_unitario": float(precio),
                        "iva": float(iva),
                        "total": float(total)
                    })

                    i += 4
                    continue

                except Exception:
                    pass

            i += 1

        datos["items"] = items
        
        # -------------------
        # Datos bancarios 
        # -------------------
        datos["pago"] = {}

        # Tomar un bloque alrededor de "DETALLES PAGO"
        pago_bloque_match = re.search(r"DETALLES PAGO:\s*(.*?)(?:\nTOTAL|\nRETENCION|\nunsitiogenial\.es|$)", texto, re.S | re.I)
        pago_bloque = pago_bloque_match.group(1) if pago_bloque_match else texto

        # Banco: puede venir en la línea siguiente
        banco_match = re.search(r"Banco:\s*([^\n]+)?(?:\n([^\n]+))?", pago_bloque, re.I)
        if banco_match:
            banco = (banco_match.group(1) or banco_match.group(2) or "").strip()
            if banco:
                datos["pago"]["banco"] = banco

        # Cuenta: buscar un número largo tipo "0123 4567 8901" (o todo junto)
        cuenta_match = re.search(r"(\d{4}\s?\d{4}\s?\d{4}(?:\s?\d{4})?)", pago_bloque)
        if cuenta_match:
            datos["pago"]["cuenta"] = re.sub(r"\s+", "", cuenta_match.group(1))

        # Vencimiento: puede estar en línea siguiente
        venc_match = re.search(r"Vencimiento:\s*(\d{2}/\d{2}/\d{4})", pago_bloque, re.I)
        if not venc_match:
            # fallback por si queda partido
            venc_match = re.search(r"Vencimiento:\s*\n\s*(\d{2}/\d{2}/\d{4})", pago_bloque, re.I)

        if venc_match:
            datos["pago"]["vencimiento"] = venc_match.group(1)


        # -------------------
        # Totales
        # -------------------
        base_match = re.search(r"BASE IMPONIBLE\s+(\d+)", texto)
        if base_match:
            datos["totales"]["base_imponible"] = self.limpiar_numero(base_match.group(1))

        iva_total_match = re.search(r"IVA.*?\n.*?\n(\d+)", texto)
        if iva_total_match:
            datos["totales"]["iva"] = float(iva_total_match.group(1))

        total_final_match = re.search(r"\n(\d+)€", texto)
        if total_final_match:
            datos["totales"]["total"] = float(total_final_match.group(1))

        return datos
