"""
shell_sort.py — ALGORITMO PROPIO DEL TRABAJO
============================================

Historia
--------
Shell Sort fue publicado por **Donald L. Shell** en julio de 1959 en el artículo
*"A High-Speed Sorting Procedure"* (Communications of the ACM, vol. 2, n.º 7).
Fue uno de los primeros algoritmos en romper la barrera de O(n²) de los métodos
simples. Su idea: el Insertion Sort es lento porque solo mueve los elementos
UNA posición a la vez; si primero se ordenan elementos que están LEJOS
(separados por un "gap" o salto), los datos llegan casi en su lugar y la pasada
final con gap = 1 es muy rápida.

Después de Shell, varios autores propusieron mejores secuencias de gaps:

==============  =====  =====================  ======================
Secuencia       Año    Gaps                   Peor caso
==============  =====  =====================  ======================
Shell           1959   n/2, n/4, ..., 1       O(n²)
Hibbard         1963   1, 3, 7, 15, ... 2^k-1 O(n^1.5)
Knuth           1973   1, 4, 13, 40, ...      O(n^1.5)
Ciura           2001   1, 4, 10, 23, 57, ...  empírica (la más rápida conocida)
==============  =====  =====================  ======================

Este proyecto usa **Knuth** por defecto (h = 3h + 1) porque tiene una cota
demostrada de O(n^1.5) y es fácil de explicar.

Características
---------------
* Por comparación: decide el orden comparando pares de elementos.
* In-place: memoria adicional O(1), ordena sobre el mismo arreglo.
* NO estable: dos valores iguales pueden quedar en orden distinto al original,
  porque un gap grande puede "saltar" un elemento por encima de su gemelo.
* Adaptativo: si los datos ya están casi ordenados, trabaja mucho menos.

Rendimiento (secuencia de Knuth)
--------------------------------
* Mejor caso  (ya ordenado):  Θ(n log n)  — cada pasada solo compara n - h veces.
* Caso promedio (aleatorio):  ≈ O(n^1.25) observado empíricamente.
* Peor caso:                  O(n^1.5) = O(n·√n).
* Espacio adicional:          O(1).

Pseudocódigo
------------
::

    SHELLSORT(A, n)
        h ← 1
        mientras h < n / 3 hacer          ▷ calcular el gap inicial (Knuth)
            h ← 3·h + 1
        mientras h ≥ 1 hacer
            para i ← h hasta n - 1 hacer   ▷ inserción con salto h
                temp ← A[i]
                j ← i
                mientras j ≥ h y A[j - h] > temp hacer
                    A[j] ← A[j - h]        ▷ desplazar h posiciones
                    j ← j - h
                A[j] ← temp
            h ← (h - 1) / 3                ▷ siguiente gap, más pequeño
        retornar A
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from .metricas import Metricas

Numero = float  # Los algoritmos ordenan cualquier valor comparable con ">".


# ---------------------------------------------------------------------------
# Secuencias de gaps
# ---------------------------------------------------------------------------

def gaps_shell(n: int) -> List[int]:
    """Secuencia original de Shell (1959): n/2, n/4, ..., 1.

    Args:
        n: tamaño del arreglo.

    Returns:
        Lista de gaps de MAYOR a MENOR, terminando siempre en 1.
    """
    gaps = []
    h = n // 2
    while h > 0:
        gaps.append(h)
        h //= 2
    return gaps or [1]


def gaps_knuth(n: int) -> List[int]:
    """Secuencia de Knuth (1973): 1, 4, 13, 40, 121, ... (h = 3h + 1).

    Igual que en el pseudocódigo: se crece h mientras h < n/3.

    Args:
        n: tamaño del arreglo.

    Returns:
        Lista de gaps de MAYOR a MENOR, terminando siempre en 1.
    """
    gaps = [1]
    while gaps[-1] < n // 3:
        gaps.append(gaps[-1] * 3 + 1)
    return gaps[::-1]


def gaps_ciura(n: int) -> List[int]:
    """Secuencia empírica de Ciura (2001), extendida multiplicando por 2.25.

    Args:
        n: tamaño del arreglo.

    Returns:
        Lista de gaps de MAYOR a MENOR, terminando siempre en 1.
    """
    gaps = [1, 4, 10, 23, 57, 132, 301, 701, 1750]
    while gaps[-1] < n:
        gaps.append(int(gaps[-1] * 2.25))
    return [g for g in gaps if g < n][::-1] or [1]


#: Secuencias disponibles, por nombre. Se usan en las gráficas comparativas.
SECUENCIAS: dict[str, Callable[[int], List[int]]] = {
    "Shell (1959)": gaps_shell,
    "Knuth (1973)": gaps_knuth,
    "Ciura (2001)": gaps_ciura,
}


# ---------------------------------------------------------------------------
# Algoritmo
# ---------------------------------------------------------------------------

def shell_sort(datos: Sequence[Numero],
               secuencia: Callable[[int], List[int]] = gaps_knuth,
               metricas: Optional[Metricas] = None) -> List[Numero]:
    """Ordena de menor a mayor usando Shell Sort.

    No modifica la secuencia recibida: trabaja sobre una copia y la retorna.

    Args:
        datos:     valores a ordenar (lista, tupla, etc.).
        secuencia: función que genera los gaps (por defecto, Knuth).
        metricas:  objeto opcional donde se acumulan comparaciones,
                   movimientos y pasadas. Si es ``None`` no se cuenta nada.

    Returns:
        Una lista nueva con los valores ordenados ascendentemente.

    Ejemplo:
        >>> shell_sort([23, 4, 15, 8, 42, 16])
        [4, 8, 15, 16, 23, 42]
    """
    arreglo = list(datos)              # copia: no se altera la entrada
    n = len(arreglo)
    if n < 2:                          # 0 o 1 elementos ya están ordenados
        return arreglo

    for h in secuencia(n):             # de gaps grandes a gap = 1
        if metricas is not None:
            metricas.pasadas += 1

        # Insertion Sort "con saltos": cada sublista separada por h se ordena.
        for i in range(h, n):
            temp = arreglo[i]
            j = i
            while j >= h:
                if metricas is not None:
                    metricas.comparaciones += 1
                if arreglo[j - h] > temp:           # ¿el de atrás es mayor?
                    arreglo[j] = arreglo[j - h]     # sí → se corre h lugares
                    if metricas is not None:
                        metricas.movimientos += 1
                    j -= h
                else:
                    break                           # ya encontró su sitio
            if j != i:
                arreglo[j] = temp                   # se deja en su posición
                if metricas is not None:
                    metricas.movimientos += 1
    return arreglo


def shell_sort_traza(datos: Sequence[Numero],
                     secuencia: Callable[[int], List[int]] = gaps_knuth
                     ) -> List[tuple[int, List[Numero]]]:
    """Ejecuta Shell Sort y guarda el estado del arreglo tras cada gap.

    Se usa en la demo paso a paso para mostrar cómo los datos se van
    "acercando" a su posición final con cada gap.

    Args:
        datos:     valores a ordenar.
        secuencia: generador de gaps.

    Returns:
        Lista de tuplas ``(gap, estado_del_arreglo_después_de_ese_gap)``.
    """
    arreglo = list(datos)
    n = len(arreglo)
    traza: List[tuple[int, List[Numero]]] = []
    if n < 2:
        return traza
    for h in secuencia(n):
        for i in range(h, n):
            temp = arreglo[i]
            j = i
            while j >= h and arreglo[j - h] > temp:
                arreglo[j] = arreglo[j - h]
                j -= h
            arreglo[j] = temp
        traza.append((h, list(arreglo)))
    return traza
