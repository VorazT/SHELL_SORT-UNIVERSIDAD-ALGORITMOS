"""
generadores.py
==============

Crea los arreglos de entrada para las pruebas y las mediciones.

Se usan tres tipos de entrada porque cada uno provoca un caso distinto:

* ``aleatorio`` → caso promedio.
* ``ordenado``  → mejor caso de los tres algoritmos.
* ``inverso``   → peor caso de Insertion Sort (orden descendente).
* ``tus datos`` → los números que escribe el usuario, repetidos como patrón
  hasta llegar al tamaño que se quiere medir.

Todos los generadores reciben una semilla para que los resultados sean
REPRODUCIBLES: ejecutar el programa dos veces produce los mismos arreglos.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List

SEMILLA = 2026


def aleatorio(n: int, semilla: int = SEMILLA) -> List[int]:
    """Enteros aleatorios entre 0 y 10·n (puede haber repetidos)."""
    rng = random.Random(semilla + n)
    return [rng.randint(0, 10 * n) for _ in range(n)]


def ordenado(n: int, semilla: int = SEMILLA) -> List[int]:
    """Enteros ya ordenados de menor a mayor: 0, 1, 2, ..., n-1."""
    return list(range(n))


def inverso(n: int, semilla: int = SEMILLA) -> List[int]:
    """Enteros en orden descendente: n, n-1, ..., 1."""
    return list(range(n, 0, -1))


def aleatorio_con_semilla(semilla: int) -> Callable[[int], List[int]]:
    """Generador aleatorio con una semilla propia (cada ejecución es distinta).

    Args:
        semilla: número que fija la secuencia aleatoria.

    Returns:
        Función ``generar(n)`` que crea ``n`` enteros aleatorios.
    """
    def generar(n: int, _semilla: int = semilla) -> List[int]:
        return aleatorio(n, _semilla)
    return generar


def desde_patron(valores: List[float]) -> Callable[[int], List[float]]:
    """Generador que usa los números del usuario como patrón.

    Con pocos números no se puede ver cómo crece el tiempo, así que se repiten
    en orden hasta formar un arreglo de tamaño ``n``. Ejemplo con el patrón
    [5, 2, 9] y n = 7 → [5, 2, 9, 5, 2, 9, 5].

    Args:
        valores: números escritos por el usuario (al menos uno).

    Returns:
        Función ``generar(n)`` que crea el arreglo de tamaño ``n``.
    """
    patron = list(valores)

    def generar(n: int, _semilla: int = SEMILLA) -> List[float]:
        return [patron[i % len(patron)] for i in range(n)]
    return generar


def tipos_de_entrada(principal: Callable[[int], List[float]],
                     nombre: str = "aleatorio") -> Dict[str, Callable]:
    """Los tres tipos de entrada, cambiando el primero por ``principal``.

    Args:
        principal: generador del caso principal (aleatorio o tus datos).
        nombre:    cómo se llama ese caso en las gráficas.
    """
    return {nombre: principal, "ordenado": ordenado, "inverso": inverso}


#: Tipos de entrada disponibles y el caso que representan.
TIPOS: Dict[str, Callable[[int, int], List[int]]] = {
    "aleatorio": aleatorio,
    "ordenado": ordenado,
    "inverso": inverso,
}

#: Color y marcador de cada caso en las gráficas de comparaciones.
ESTILO_CASO = {
    "aleatorio": ("#6250d6", "o"),
    "tus datos": ("#6250d6", "o"),
    "ordenado": ("#008300", "s"),
    "inverso": ("#e34948", "^"),
}


def tamanos(n_min: int, n_max: int, puntos: int) -> List[int]:
    """Rango creciente de tamaños de arreglo, igualmente espaciados.

    Args:
        n_min:  tamaño más pequeño.
        n_max:  tamaño más grande.
        puntos: cuántos tamaños generar (mínimo 2).

    Returns:
        Lista ordenada de tamaños sin repetidos, p. ej. [200, 400, ..., 3000].
    """
    if puntos < 2 or n_max <= n_min:
        return [n_max]
    paso = (n_max - n_min) / (puntos - 1)
    return sorted({int(round(n_min + i * paso)) for i in range(puntos)})
