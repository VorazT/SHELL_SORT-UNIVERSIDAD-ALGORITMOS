"""
heap_sort.py — ALGORITMO DE COMPARACIÓN N.º 2 (el "rival" de Shell Sort)
========================================================================

¿Por qué se eligió para comparar?
---------------------------------
De la lista de métodos del curso, Heap Sort es el que tiene el MISMO perfil
que Shell Sort: ordena dentro del mismo arreglo (memoria O(1)), no es estable
y es mucho más rápido que los métodos O(n²). La diferencia está en la garantía:
Heap Sort asegura Θ(n log n) SIEMPRE, mientras que Shell Sort depende de la
secuencia de gaps. Compararlos responde: ¿vale la pena la garantía teórica, o
la sencillez de Shell Sort gana en la práctica?

Historia
--------
Lo publicó **J. W. J. Williams** en 1964 (Communications of the ACM,
"Algorithm 232: Heapsort"), junto con la estructura de datos *heap* (montículo
binario). Ese mismo año **Robert W. Floyd** ("Algorithm 245: Treesort 3")
mejoró la construcción del heap para hacerla en tiempo O(n), que es la versión
que se usa hoy.

Características
---------------
* Por comparación, basado en una estructura de datos: el heap máximo
  (cada padre es mayor o igual que sus hijos; el mayor queda en la raíz).
* El heap se guarda DENTRO del mismo arreglo: los hijos de la posición i están
  en 2i + 1 y 2i + 2. Por eso es in-place, memoria adicional O(1).
* NO estable.
* NO adaptativo: tarda casi lo mismo aunque los datos ya estén ordenados.

Rendimiento
-----------
* Mejor caso:        Θ(n log n)  (con claves distintas).
* Caso promedio:     Θ(n log n).
* Peor caso:         Θ(n log n)  — garantizado, no hay caso malo.
* Espacio adicional: O(1).
* Construir el heap cuesta O(n); cada una de las n extracciones, O(log n).

Pseudocódigo
------------
::

    HEAPSORT(A, n)
        para i ← piso(n / 2) - 1 bajando hasta 0 hacer     ▷ 1. construir heap
            HUNDIR(A, i, n)
        para fin ← n - 1 bajando hasta 1 hacer             ▷ 2. extraer máximos
            intercambiar A[0], A[fin]                      ▷ el mayor va al final
            HUNDIR(A, 0, fin)                              ▷ reparar el heap
        retornar A

    HUNDIR(A, i, tamaño)
        mientras 2·i + 1 < tamaño hacer
            hijo ← 2·i + 1                                 ▷ hijo izquierdo
            si hijo + 1 < tamaño y A[hijo + 1] > A[hijo] entonces
                hijo ← hijo + 1                            ▷ el hijo mayor
            si A[hijo] > A[i] entonces
                intercambiar A[i], A[hijo]
                i ← hijo
            si no
                terminar
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from .metricas import Metricas


def _hundir(arreglo: List, i: int, tamano: int,
            metricas: Optional[Metricas]) -> None:
    """Baja el elemento de la posición ``i`` hasta que cumpla la regla del heap.

    Args:
        arreglo:  arreglo que contiene el heap.
        i:        posición del elemento que puede estar "fuera de lugar".
        tamano:   cuántas posiciones (desde 0) forman parte del heap.
        metricas: contador opcional de operaciones.
    """
    while 2 * i + 1 < tamano:
        hijo = 2 * i + 1                              # hijo izquierdo
        if hijo + 1 < tamano:
            if metricas is not None:
                metricas.comparaciones += 1
            if arreglo[hijo + 1] > arreglo[hijo]:     # ¿el derecho es mayor?
                hijo += 1
        if metricas is not None:
            metricas.comparaciones += 1
        if arreglo[hijo] > arreglo[i]:                # el hijo mayor sube
            arreglo[i], arreglo[hijo] = arreglo[hijo], arreglo[i]
            if metricas is not None:
                metricas.movimientos += 2
            i = hijo
        else:
            break                                     # ya cumple la regla


def heap_sort(datos: Sequence,
              metricas: Optional[Metricas] = None) -> List:
    """Ordena de menor a mayor usando Heap Sort.

    No modifica la secuencia recibida: trabaja sobre una copia y la retorna.

    Args:
        datos:    valores a ordenar.
        metricas: objeto opcional donde se acumulan las operaciones.

    Returns:
        Una lista nueva con los valores ordenados ascendentemente.

    Ejemplo:
        >>> heap_sort([12, 11, 13, 5, 6, 7])
        [5, 6, 7, 11, 12, 13]
    """
    arreglo = list(datos)
    n = len(arreglo)

    # 1. Construir el heap máximo (método de Floyd, O(n)).
    for i in range(n // 2 - 1, -1, -1):
        _hundir(arreglo, i, n, metricas)

    # 2. Sacar el máximo (raíz) y llevarlo al final, n - 1 veces.
    for fin in range(n - 1, 0, -1):
        arreglo[0], arreglo[fin] = arreglo[fin], arreglo[0]
        if metricas is not None:
            metricas.movimientos += 2
            metricas.pasadas += 1
        _hundir(arreglo, 0, fin, metricas)
    return arreglo
