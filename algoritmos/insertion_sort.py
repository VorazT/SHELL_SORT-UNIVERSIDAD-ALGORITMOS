"""
insertion_sort.py — ALGORITMO DE COMPARACIÓN N.º 1 ("el papá" de Shell Sort)
============================================================================

¿Por qué se eligió para comparar?
---------------------------------
Shell Sort ES un Insertion Sort mejorado: cuando el gap llega a 1, Shell Sort
hace exactamente un Insertion Sort. Compararlos muestra directamente cuánto
ganan los gaps grandes.

Historia
--------
Es uno de los métodos más antiguos: es la forma en que una persona ordena las
cartas de una mano. En computación aparece desde los inicios; Knuth (The Art of
Computer Programming, vol. 3) señala que John Mauchly ya discutió la inserción
en 1946, en las conferencias de la Moore School sobre los primeros
computadores electrónicos.

Características
---------------
* Por comparación.
* In-place: memoria adicional O(1).
* Estable: los valores iguales conservan su orden original.
* Adaptativo: casi lineal si los datos vienen casi ordenados.
* Online: puede ordenar datos a medida que van llegando.

Rendimiento
-----------
* Mejor caso  (ya ordenado):   Θ(n)   — n - 1 comparaciones.
* Caso promedio (aleatorio):   Θ(n²)  — ≈ n²/4 comparaciones.
* Peor caso   (orden inverso): Θ(n²)  — n(n - 1)/2 comparaciones.
* Espacio adicional:           O(1).

Pseudocódigo
------------
::

    INSERTIONSORT(A, n)
        para i ← 1 hasta n - 1 hacer
            temp ← A[i]                     ▷ elemento a insertar
            j ← i
            mientras j > 0 y A[j - 1] > temp hacer
                A[j] ← A[j - 1]             ▷ desplazar 1 posición
                j ← j - 1
            A[j] ← temp
        retornar A
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from .metricas import Metricas


def insertion_sort(datos: Sequence,
                   metricas: Optional[Metricas] = None) -> List:
    """Ordena de menor a mayor usando Insertion Sort.

    No modifica la secuencia recibida: trabaja sobre una copia y la retorna.

    Args:
        datos:    valores a ordenar.
        metricas: objeto opcional donde se acumulan las operaciones.

    Returns:
        Una lista nueva con los valores ordenados ascendentemente.

    Ejemplo:
        >>> insertion_sort([5, 2, 9, 1])
        [1, 2, 5, 9]
    """
    arreglo = list(datos)
    n = len(arreglo)
    if metricas is not None:
        metricas.pasadas += 1 if n > 1 else 0

    for i in range(1, n):
        temp = arreglo[i]                 # la "carta" que se va a insertar
        j = i
        while j > 0:
            if metricas is not None:
                metricas.comparaciones += 1
            if arreglo[j - 1] > temp:
                arreglo[j] = arreglo[j - 1]   # se corre una posición
                if metricas is not None:
                    metricas.movimientos += 1
                j -= 1
            else:
                break
        if j != i:
            arreglo[j] = temp
            if metricas is not None:
                metricas.movimientos += 1
    return arreglo
