"""
complejidad.py
==============

Funciones teóricas f(n) de la notación Big O y el ajuste de la constante c.

La notación Big O dice que el costo T(n) crece como c·f(n) para alguna
constante c. El programa mide T(n) (comparaciones o tiempo) y calcula la c que
mejor acerca c·f(n) a los datos con MÍNIMOS CUADRADOS:

    c = Σ T(n)·f(n) / Σ f(n)²

Luego reporta R² (coeficiente de determinación): entre más cerca de 1, mejor
describe f(n) el crecimiento real. Así la gráfica no solo "dibuja" la curva
teórica: la COMPARA con lo medido.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Sequence, Tuple


@dataclass(frozen=True)
class Modelo:
    """Una función de crecimiento f(n) con su etiqueta para las gráficas."""

    etiqueta: str
    f: Callable[[float], float]


# Funciones de crecimiento más comunes -------------------------------------
N = Modelo("n", lambda n: n)
N_LOG_N = Modelo("n·log₂n", lambda n: n * math.log2(n))
N_1_25 = Modelo("n^1.25", lambda n: n ** 1.25)
N_1_5 = Modelo("n^1.5", lambda n: n ** 1.5)
N_2 = Modelo("n²", lambda n: n ** 2)

#: Modelo teórico que se espera para cada algoritmo y tipo de entrada.
#: Insertion Sort tiene fórmulas exactas; Shell y Heap, cotas asintóticas.
MODELOS: Dict[str, Dict[str, Modelo]] = {
    "shell": {"ordenado": N_LOG_N, "aleatorio": N_1_25, "inverso": N_1_25},
    "insertion": {"ordenado": N, "aleatorio": N_2, "inverso": N_2},
    "heap": {"ordenado": N_LOG_N, "aleatorio": N_LOG_N, "inverso": N_LOG_N},
}

#: Curvas que se dibujan juntas en la gráfica de "funciones teóricas".
REFERENCIA = [N, N_LOG_N, N_1_25, N_1_5, N_2]


def ajustar(ns: Sequence[int], ys: Sequence[float],
            modelo: Modelo) -> Tuple[float, float]:
    """Ajusta y ≈ c·f(n) por mínimos cuadrados.

    Args:
        ns:     tamaños de arreglo medidos.
        ys:     valor medido para cada tamaño (comparaciones o tiempo).
        modelo: función de crecimiento f(n) a probar.

    Returns:
        ``(c, r2)``: la constante ajustada y el coeficiente R² del ajuste.
    """
    fs = [modelo.f(n) for n in ns]
    denominador = sum(f * f for f in fs)
    if denominador == 0:
        return 0.0, 0.0
    c = sum(y * f for y, f in zip(ys, fs)) / denominador

    media = sum(ys) / len(ys)
    ss_total = sum((y - media) ** 2 for y in ys)
    ss_residuo = sum((y - c * f) ** 2 for y, f in zip(ys, fs))
    r2 = 1 - ss_residuo / ss_total if ss_total > 0 else 1.0
    return c, r2
