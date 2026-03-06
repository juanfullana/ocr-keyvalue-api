import cv2
import numpy as np


def dibujar_cajas(imagen, resultados):

    img = imagen.copy()

    for bbox, texto, conf in resultados:

        pts = np.array(bbox).astype(int)

        cv2.polylines(
            img,
            [pts],
            isClosed=True,
            color=(0,255,0),
            thickness=2
        )

        x, y = pts[0]

        cv2.putText(
            img,
            texto,
            (x, y-5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0,255,0),
            1,
            cv2.LINE_AA
        )

    return img