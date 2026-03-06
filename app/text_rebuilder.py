def reconstruir_lineas(resultados, tolerancia_y=15):
    
    lineas = []

    for bbox, texto, conf in resultados:

        y = bbox[0][1]

        agregado = False

        for linea in lineas:

            if abs(linea["y"] - y) < tolerancia_y:
                linea["palabras"].append((bbox[0][0], texto))
                agregado = True
                break

        if not agregado:
            lineas.append({
                "y": y,
                "palabras": [(bbox[0][0], texto)]
            })

    # ordenar palabras dentro de cada linea
    texto_final = []

    for linea in sorted(lineas, key=lambda l: l["y"]):

        palabras_ordenadas = sorted(linea["palabras"], key=lambda p: p[0])

        linea_texto = " ".join([p[1] for p in palabras_ordenadas])

        texto_final.append(linea_texto)

    return "\n".join(texto_final)