"""Pruebas unitarias de Heap Sort."""

import math
from collections import Counter

import pytest

from algoritmos import Metricas, heap_sort
from algoritmos.heap_sort import _hundir
from tests.comun import CASOS_BORDE, Clave, arreglos_aleatorios


@pytest.mark.parametrize("nombre,entrada", CASOS_BORDE)
def test_casos_borde(nombre, entrada):
    assert heap_sort(entrada) == sorted(entrada)


def test_aleatorios_ordenados_y_permutacion():
    for entrada in arreglos_aleatorios():
        salida = heap_sort(entrada)
        assert salida == sorted(entrada)
        assert Counter(salida) == Counter(entrada)


def test_no_modifica_la_entrada():
    entrada = [4, 3, 2, 1]
    heap_sort(entrada)
    assert entrada == [4, 3, 2, 1]


def test_hundir_construye_un_heap_maximo():
    """Tras construir el heap, cada padre es >= que sus hijos."""
    arreglo = [3, 9, 2, 1, 4, 5, 8, 7, 6]
    n = len(arreglo)
    for i in range(n // 2 - 1, -1, -1):
        _hundir(arreglo, i, n, None)
    for i in range(n):
        for hijo in (2 * i + 1, 2 * i + 2):
            if hijo < n:
                assert arreglo[i] >= arreglo[hijo]
    assert arreglo[0] == max(arreglo)


@pytest.mark.parametrize("tipo", ["ordenado", "inverso", "aleatorio"])
@pytest.mark.parametrize("n", [16, 256, 2048])
def test_comparaciones_dentro_de_2_n_log_n(tipo, n):
    """Θ(n log n) en TODOS los casos: la cota se cumple con cualquier entrada."""
    entradas = {"ordenado": list(range(n)), "inverso": list(range(n, 0, -1)),
                "aleatorio": next(arreglos_aleatorios(1, semilla=n))}
    entrada = entradas[tipo]
    m = Metricas()
    heap_sort(entrada, metricas=m)
    tamano = len(entrada)
    if tamano > 1:
        assert m.comparaciones <= 2 * tamano * math.log2(tamano)


def test_no_es_adaptativo():
    """A diferencia de Shell e Insertion, ordenado o no cuesta casi lo mismo."""
    n = 2000
    m_ord, m_inv = Metricas(), Metricas()
    heap_sort(list(range(n)), metricas=m_ord)
    heap_sort(list(range(n, 0, -1)), metricas=m_inv)
    assert 0.8 < m_ord.comparaciones / m_inv.comparaciones < 1.25


def test_no_es_estable():
    datos = [Clave(c, i) for i, c in enumerate([1, 1, 1, 0, 0])]
    salida = heap_sort(datos)
    assert any(a.clave == b.clave and a.origen > b.origen
               for a, b in zip(salida, salida[1:]))
