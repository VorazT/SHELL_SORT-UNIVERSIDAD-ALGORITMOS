"""
visor.py
========

Abre una ventana para ver las gráficas generadas, una a la vez.

* Botones **◀ Anterior** y **Siguiente ▶** (o las flechas del teclado).
* Al cerrar la ventana, el programa vuelve al menú.

Las gráficas se dibujan con el motor "Agg" (sin ventanas, más rápido) y aquí
se cambia a un motor con ventana (TkAgg, que viene con Python en Windows).
Si el computador no puede abrir ventanas, se informa dónde quedaron los PNG.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

#: Orden y descripción de cada gráfica en el visor.
GRAFICAS: List[Tuple[str, str]] = [
    ("shell_analisis.png", "Shell Sort: lo medido frente a su f(n)"),
    ("insertion_analisis.png", "Insertion Sort: lo medido frente a su f(n)"),
    ("heap_analisis.png", "Heap Sort: lo medido frente a su f(n)"),
    ("comparacion_tiempo.png", "Comparación del tiempo de los tres"),
    ("comparacion_operaciones.png", "Comparación de las comparaciones de los tres"),
    ("rango_ampliado.png", "Rango ampliado: arreglos mucho más grandes"),
    ("shell_secuencias_gaps.png", "Shell Sort con distintas secuencias de gaps"),
    ("funciones_teoricas.png", "Funciones de crecimiento f(n) de Big O"),
]

FONDO = "#fcfcfb"
TINTA = "#0b0b0b"
AZUL = "#2a78d6"


def _activar_ventanas() -> bool:
    """Cambia a un motor de matplotlib que abra ventanas.

    Returns:
        True si se pudo; False si el computador no permite abrir ventanas.
    """
    for motor in ("TkAgg", "QtAgg", "MacOSX"):
        try:
            plt.switch_backend(motor)
            return True
        except Exception:      # motor no instalado o sin pantalla
            continue
    return False


def mostrar(carpeta: Path) -> bool:
    """Muestra las gráficas de ``carpeta`` en una ventana con botones.

    Args:
        carpeta: carpeta donde están los PNG generados.

    Returns:
        True si se abrió la ventana; False si no había gráficas o no se pudo.
    """
    lista = [(carpeta / archivo, texto) for archivo, texto in GRAFICAS
             if (carpeta / archivo).exists()]
    if not lista:
        print("  Todavía no hay gráficas. Usa primero la opción 3 del menú.")
        return False
    motor_anterior = matplotlib.get_backend()
    if not _activar_ventanas():
        print(f"  No se pudo abrir una ventana. Las gráficas están en: {carpeta}")
        return False

    fig = plt.figure(figsize=(13.5, 7.8), facecolor=FONDO)
    try:
        fig.canvas.manager.set_window_title(
            "Gráficas — Shell Sort vs Insertion Sort vs Heap Sort")
    except Exception:
        pass
    eje = fig.add_axes((0.01, 0.09, 0.98, 0.84))
    estado = {"i": 0}

    def pintar() -> None:
        ruta, texto = lista[estado["i"]]
        eje.clear()
        eje.axis("off")
        eje.imshow(mpimg.imread(ruta))
        fig.suptitle(f"Gráfica {estado['i'] + 1} de {len(lista)}  ·  {texto}",
                     fontsize=13, fontweight="bold", color=TINTA, y=0.975)
        fig.canvas.draw_idle()

    def mover(paso: int) -> None:
        estado["i"] = (estado["i"] + paso) % len(lista)
        pintar()

    eje_ant = fig.add_axes((0.32, 0.015, 0.16, 0.055))
    eje_sig = fig.add_axes((0.52, 0.015, 0.16, 0.055))
    boton_ant = Button(eje_ant, "◀  Anterior", color="#e9edf4", hovercolor="#d6dde8")
    boton_sig = Button(eje_sig, "Siguiente  ▶", color=AZUL, hovercolor="#1f66bd")
    boton_sig.label.set_color("white")
    for boton in (boton_ant, boton_sig):
        boton.label.set_fontsize(11)
        boton.label.set_fontweight("bold")
    boton_ant.on_clicked(lambda _: mover(-1))
    boton_sig.on_clicked(lambda _: mover(1))
    fig.canvas.mpl_connect(
        "key_press_event",
        lambda e: mover(1) if e.key in ("right", " ") else
        mover(-1) if e.key == "left" else None)

    pintar()
    print(f"\n  Se abrió una ventana con {len(lista)} gráficas:")
    print("    · Botones ◀ Anterior / Siguiente ▶ (o las flechas del teclado)")
    print("    · Cierra la ventana para volver al menú")
    plt.show()                 # espera hasta que el usuario cierre la ventana
    plt.close("all")
    try:
        plt.switch_backend(motor_anterior)
    except Exception:
        pass
    # Se guardan referencias a los botones para que no se borren antes de tiempo.
    del boton_ant, boton_sig
    return True
