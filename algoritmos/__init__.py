"""
Paquete ``algoritmos``
======================

Reúne los tres métodos de ordenamiento del proyecto y una ficha con los datos
que usan las pruebas, el verificador de calidad y las gráficas.

* Shell Sort      → algoritmo propio del trabajo.
* Insertion Sort  → su base: Shell Sort con gap = 1.
* Heap Sort       → mismo perfil (in-place, no estable), pero Θ(n log n)
                    garantizado gracias a un heap.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from .heap_sort import heap_sort
from .insertion_sort import insertion_sort
from .metricas import Metricas
from .shell_sort import gaps_ciura, gaps_knuth, gaps_shell, shell_sort


@dataclass(frozen=True)
class FichaAlgoritmo:
    """Información de un algoritmo para el análisis y las gráficas.

    Attributes:
        nombre:   nombre para mostrar.
        clave:    identificador corto (se usa en nombres de archivo).
        funcion:  función ``f(datos, metricas=None) -> lista_ordenada``.
        estable:  True si conserva el orden de los valores iguales.
        color:    color de la serie en todas las gráficas.
        mejor, promedio, peor: notación Big O de cada caso (texto).
    """

    nombre: str
    clave: str
    funcion: Callable[..., List]
    estable: bool
    color: str
    mejor: str
    promedio: str
    peor: str


ALGORITMOS: List[FichaAlgoritmo] = [
    FichaAlgoritmo("Shell Sort", "shell", shell_sort, False, "#2a78d6",
                   "Θ(n log n)", "≈ O(n^1.25)", "O(n^1.5)"),
    FichaAlgoritmo("Insertion Sort", "insertion", insertion_sort, True,
                   "#eb6834", "Θ(n)", "Θ(n²)", "Θ(n²)"),
    FichaAlgoritmo("Heap Sort", "heap", heap_sort, False, "#1baf7a",
                   "Θ(n log n)", "Θ(n log n)", "Θ(n log n)"),
]


def buscar(clave: str) -> FichaAlgoritmo:
    """Devuelve la ficha cuyo ``clave`` coincide (shell, insertion o heap)."""
    for ficha in ALGORITMOS:
        if ficha.clave == clave:
            return ficha
    raise KeyError(f"Algoritmo desconocido: {clave!r}")


__all__ = [
    "ALGORITMOS", "FichaAlgoritmo", "Metricas", "buscar",
    "shell_sort", "insertion_sort", "heap_sort",
    "gaps_shell", "gaps_knuth", "gaps_ciura",
]
