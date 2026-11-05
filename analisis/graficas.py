"""
graficas.py
===========

Genera TODAS las gráficas del proyecto con matplotlib. Cada gráfica la produce
el mismo programa a partir de las mediciones de ``benchmark.py``.

Gráficas generadas (carpeta ``resultados/graficas``):

=================================  =============================================
Archivo                            Qué muestra
=================================  =============================================
funciones_teoricas.png             Las funciones f(n) de Big O, solas.
<algoritmo>_analisis.png           Por algoritmo: comparaciones de cada caso vs
                                   c·f(n) ajustada, y tiempo real vs c·f(n).
comparacion_tiempo.png             Tiempo de los 3 algoritmos (aleatorio).
comparacion_operaciones.png        Comparaciones de los 3 (escala logarítmica).
rango_ampliado.png                 Tiempo con arreglos mucho más grandes.
shell_secuencias_gaps.png          Shell Sort con las secuencias de gaps.
=================================  =============================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")                    # dibuja a archivo, sin abrir ventanas
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.lines import Line2D     # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from algoritmos import FichaAlgoritmo    # noqa: E402

from .complejidad import MODELOS, REFERENCIA, Modelo, ajustar  # noqa: E402
from .generadores import ESTILO_CASO     # noqa: E402

# Paleta y estilo (validada para daltonismo) --------------------------------
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_3 = "#8a8984"
REJILLA = "#e6e5e1"
TEORICA = "#52514e"              # las curvas c·f(n) van en gris punteado

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "axes.edgecolor": REJILLA,
    "axes.labelcolor": TINTA_2,
    "axes.titlecolor": TINTA,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": REJILLA,
    "grid.linewidth": 0.8,
    "xtick.color": TINTA_3,
    "ytick.color": TINTA_3,
    "xtick.labelcolor": TINTA_2,
    "ytick.labelcolor": TINTA_2,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "savefig.dpi": 160,
})

_MILES = FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", "."))


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _etiquetas_directas(ax, items: List[Tuple[float, float, str, str]],
                        separacion_px: float = 24) -> None:
    """Pone una etiqueta al final de cada línea, sin que se encimen.

    Args:
        ax:    ejes de matplotlib.
        items: tuplas ``(x, y, texto, color)`` del último punto de cada serie.
        separacion_px: distancia vertical mínima entre etiquetas, en píxeles.
    """
    fig = ax.figure
    fig.canvas.draw()
    trans = ax.transData
    puntos = sorted(((trans.transform((x, y))[1], x, y, t, c)
                     for x, y, t, c in items), key=lambda p: p[0])
    ys_px: List[float] = []
    for y_px, *_ in puntos:
        y_nuevo = y_px if not ys_px else max(y_px, ys_px[-1] + separacion_px)
        ys_px.append(y_nuevo)
    a_puntos = 72 / fig.dpi                 # píxeles → puntos tipográficos
    for (y_px, x, y, texto, color), y_eti in zip(puntos, ys_px):
        # Desplazamiento en puntos: no cambia si después se ajusta el layout.
        ax.annotate(texto, xy=(x, y),
                    xytext=(10, (y_eti - y_px) * a_puntos),
                    textcoords="offset points", fontsize=8.5,
                    color=TINTA, va="center", ha="left",
                    arrowprops=dict(arrowstyle="-", color=color, lw=1.5,
                                    shrinkA=0, shrinkB=3))


def _guardar(fig, carpeta: Path, nombre: str) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    fig.savefig(ruta, bbox_inches="tight", facecolor=SUPERFICIE)
    plt.close(fig)
    return ruta


def _formato_c(c: float) -> str:
    """Muestra la constante c con pocas cifras (0.25, 1.3e-05, ...)."""
    return f"{c:.3g}" if c >= 1e-3 else f"{c:.2e}"


# ---------------------------------------------------------------------------
# 1. Funciones teóricas
# ---------------------------------------------------------------------------

def grafica_funciones_teoricas(carpeta: Path, n_max: int = 60) -> Path:
    """Dibuja las funciones f(n) de Big O que se usan en el análisis."""
    ns = list(range(2, n_max + 1))
    # n·log n en el color de Heap, n^1.25 en el de Shell, n² en el de Insertion
    colores = ["#008300", "#1baf7a", "#2a78d6", "#6250d6", "#eb6834"]
    fig, ax = plt.subplots(figsize=(9, 5))
    finales = []
    for modelo, color in zip(REFERENCIA, colores):
        ys = [modelo.f(n) for n in ns]
        ax.plot(ns, ys, color=color, lw=2, label=f"f(n) = {modelo.etiqueta}")
        finales.append((ns[-1], ys[-1], modelo.etiqueta, color))
    ax.set_ylim(0, REFERENCIA[3].f(n_max) * 1.6)
    ax.set_xlim(0, n_max * 1.12)
    ax.set_title("Funciones de crecimiento f(n) de la notación Big O")
    ax.set_xlabel("n (cantidad de elementos)")
    ax.set_ylabel("f(n) — operaciones")
    ax.legend(loc="upper left")
    tope = ax.get_ylim()[1]
    etiquetas = []
    for x, y, texto, color in finales:
        if y <= tope:
            etiquetas.append((x, y, texto, color))
        else:   # se etiqueta donde la curva sale por arriba
            modelo = next(m for m in REFERENCIA if m.etiqueta == texto)
            x_sal = max(n for n in ns if modelo.f(n) <= tope)
            ax.annotate(f"{texto} ↑", xy=(x_sal, modelo.f(x_sal)),
                        xytext=(8, -4), textcoords="offset points",
                        fontsize=8.5, color=TINTA, va="top")
    _etiquetas_directas(ax, etiquetas)
    ax.text(0.99, 0.02, "n² sale de la escala: crece mucho más rápido",
            transform=ax.transAxes, ha="right", fontsize=8.5, color=TINTA_2)
    return _guardar(fig, carpeta, "funciones_teoricas.png")


# ---------------------------------------------------------------------------
# 2. Análisis individual de cada algoritmo
# ---------------------------------------------------------------------------

def grafica_algoritmo(ficha: FichaAlgoritmo, ns: Sequence[int],
                      operaciones: Dict[str, List[float]],
                      tiempos: List[float], carpeta: Path) -> Dict[str, dict]:
    """Gráfica de dos paneles de un algoritmo y su ajuste a f(n).

    Panel izquierdo: comparaciones contadas en cada caso (puntos) frente a
    la curva teórica c·f(n) ajustada (línea punteada).
    Panel derecho: tiempo real con entrada aleatoria frente a c·f(n).

    Returns:
        Diccionario con la constante c y el R² de cada ajuste (para el informe).
    """
    modelos = MODELOS[ficha.clave]
    resumen: Dict[str, dict] = {}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.4))

    # --- Panel 1: comparaciones por caso -----------------------------------
    finales = []
    x_fino = _rango_fino(ns)
    for caso, valores in operaciones.items():
        color, marcador = ESTILO_CASO[caso]
        modelo = modelos[caso]
        c, r2 = ajustar(ns, valores, modelo)
        resumen[caso] = {"modelo": modelo.etiqueta, "c": c, "r2": r2}
        ax1.plot(x_fino, [c * modelo.f(n) for n in x_fino], color=color,
                 lw=1.5, ls="--", alpha=0.9)
        ax1.plot(ns, valores, ls="none", marker=marcador, ms=6, color=color,
                 markeredgecolor=SUPERFICIE, markeredgewidth=1,
                 label=f"{caso} (medido)")
        finales.append((ns[-1], valores[-1],
                        f"{caso}: {_formato_c(c)}·{modelo.etiqueta}  R²={r2:.3f}",
                        color))
    ax1.set_title("Comparaciones contadas vs. c·f(n)")
    ax1.set_xlabel("n (tamaño del arreglo)")
    ax1.set_ylabel("comparaciones")
    ax1.yaxis.set_major_formatter(_MILES)
    ax1.xaxis.set_major_formatter(_MILES)
    ax1.set_xlim(0, ns[-1] * 1.8)
    manijas, textos = ax1.get_legend_handles_labels()
    manijas.append(Line2D([], [], color=TEORICA, lw=1.5, ls="--"))
    textos.append("c·f(n) teórica ajustada")
    ax1.legend(manijas, textos, loc="upper left", fontsize=8.5)

    # --- Panel 2: tiempo ----------------------------------------------------
    modelo_t = modelos["aleatorio"]
    c_t, r2_t = ajustar(ns, tiempos, modelo_t)
    resumen["tiempo"] = {"modelo": modelo_t.etiqueta, "c": c_t, "r2": r2_t}
    ax2.plot(x_fino, [c_t * modelo_t.f(n) for n in x_fino], color=TEORICA,
             lw=1.8, ls="--", label=f"teórico: c·{modelo_t.etiqueta}")
    ax2.plot(ns, tiempos, color=ficha.color, lw=2, marker="o", ms=6,
             markeredgecolor=SUPERFICIE, label="tiempo medido (aleatorio)")
    ax2.set_title("Tiempo real (entrada aleatoria) vs. c·f(n)")
    ax2.set_xlabel("n (tamaño del arreglo)")
    ax2.set_ylabel("tiempo (ms)")
    ax2.xaxis.set_major_formatter(_MILES)
    ax2.legend(loc="upper left")
    ax2.text(0.98, 0.04, f"f(n) = {modelo_t.etiqueta}    R² = {r2_t:.4f}",
             transform=ax2.transAxes, ha="right", fontsize=9.5, color=TINTA,
             bbox=dict(boxstyle="round,pad=0.4", fc="#f1f0ec", ec=REJILLA))

    fig.suptitle(f"{ficha.nombre}   ·   mejor {ficha.mejor}   ·   "
                 f"promedio {ficha.promedio}   ·   peor {ficha.peor}",
                 x=0.01, ha="left", fontsize=14, fontweight="bold", color=TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _etiquetas_directas(ax1, finales, separacion_px=44)   # tras el layout
    _guardar(fig, carpeta, f"{ficha.clave}_analisis.png")
    return resumen


def _rango_fino(ns: Sequence[int], puntos: int = 120) -> List[float]:
    """Muchos puntos entre el primer y el último n, para curvas suaves."""
    inicio, fin = ns[0], ns[-1]
    return [inicio + (fin - inicio) * i / (puntos - 1) for i in range(puntos)]


# ---------------------------------------------------------------------------
# 3. Comparación entre los tres algoritmos
# ---------------------------------------------------------------------------

def grafica_comparacion(fichas: Sequence[FichaAlgoritmo], ns: Sequence[int],
                        valores: Dict[str, List[float]], carpeta: Path,
                        nombre: str, titulo: str, eje_y: str,
                        log: bool = False, recorte: Optional[float] = None,
                        nota: str = "") -> Path:
    """Líneas de los tres algoritmos sobre el mismo eje.

    Args:
        valores: clave del algoritmo → valores (pueden ser menos que ``ns`` si
                 un algoritmo se dejó de medir por lento).
        log:     usa escala logarítmica en y.
        recorte: valor máximo del eje y (las series que lo pasan "salen").
        nota:    texto pequeño en la esquina inferior derecha.
    """
    fig, ax = plt.subplots(figsize=(10, 5.4))
    finales = []
    for ficha in fichas:
        ys = valores[ficha.clave]
        xs = list(ns)[:len(ys)]
        ax.plot(xs, ys, color=ficha.color, lw=2, marker="o", ms=5,
                markeredgecolor=SUPERFICIE, label=f"{ficha.nombre}  ({ficha.promedio})")
        if recorte is None or ys[-1] <= recorte:
            finales.append((xs[-1], ys[-1], ficha.nombre, ficha.color))
        else:   # etiqueta en el último punto que sí se ve
            visibles = [(x, y) for x, y in zip(xs, ys) if y <= recorte]
            if visibles:
                x_v, y_v = visibles[-1]
                finales.append((x_v, y_v, f"{ficha.nombre} ↑ sale de la escala",
                                ficha.color))
    if log:
        ax.set_yscale("log")
        maximo = max(max(v) for v in valores.values())
        ax.set_ylim(top=maximo * 12)       # espacio para la leyenda
    else:
        ax.yaxis.set_major_formatter(_MILES)
    if recorte is not None:
        ax.set_ylim(0, recorte)
    ax.xaxis.set_major_formatter(_MILES)
    ax.set_xlim(0, ns[-1] * 1.25)
    ax.set_title(titulo)
    ax.set_xlabel("n (tamaño del arreglo)")
    ax.set_ylabel(eje_y)
    ax.legend(loc="upper left")
    _etiquetas_directas(ax, finales)
    if nota:
        ax.text(0.99, 0.02, nota, transform=ax.transAxes, ha="right",
                fontsize=8.5, color=TINTA_2)
    return _guardar(fig, carpeta, nombre)


def grafica_secuencias_gaps(ns: Sequence[int], series: Dict[str, List[float]],
                            carpeta: Path) -> Path:
    """Shell Sort con las tres secuencias de gaps (entrada aleatoria)."""
    colores = ["#6250d6", "#2a78d6", "#e87ba4"]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    finales = []
    for (nombre, ys), color in zip(series.items(), colores):
        ax.plot(ns, ys, color=color, lw=2, marker="o", ms=5,
                markeredgecolor=SUPERFICIE, label=nombre)
        finales.append((ns[-1], ys[-1], nombre, color))
    ax.yaxis.set_major_formatter(_MILES)
    ax.xaxis.set_major_formatter(_MILES)
    ax.set_xlim(0, ns[-1] * 1.22)
    ax.set_title("Shell Sort: la secuencia de gaps cambia el rendimiento")
    ax.set_xlabel("n (tamaño del arreglo)")
    ax.set_ylabel("comparaciones (entrada aleatoria)")
    ax.legend(loc="upper left")
    _etiquetas_directas(ax, finales)
    return _guardar(fig, carpeta, "shell_secuencias_gaps.png")


__all__ = ["grafica_funciones_teoricas", "grafica_algoritmo",
           "grafica_comparacion", "grafica_secuencias_gaps", "Modelo"]
