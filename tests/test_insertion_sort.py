"""Pruebas unitarias de Insertion Sort."""

from collections import Counter

import pytest

from algoritmos import Metricas, insertion_sort
from tests.comun import CASOS_BORDE, Clave, arreglos_aleatorios


@pytest.mark.parametrize("nombre,entrada", CASOS_BORDE)
def test_casos_borde(nombre, entrada):
    assert insertion_sort(entrada) == sorted(entrada)


def test_aleatorios_ordenados_y_permutacion():
    for entrada in arreglos_aleatorios():
        salida = insertion_sort(entrada)
        assert salida == sorted(entrada)
        assert Counter(salida) == Counter(entrada)


def test_no_modifica_la_entrada():
    entrada = [3, 2, 1]
    insertion_sort(entrada)
    assert entrada == [3, 2, 1]


@pytest.mark.parametrize("n", [1, 10, 500])
def test_mejor_caso_n_menos_1_comparaciones(n):
    m = Metricas()
    insertion_sort(list(range(n)), metricas=m)
    assert m.comparaciones == n - 1


@pytest.mark.parametrize("n", [2, 10, 500])
def test_peor_caso_n_n_menos_1_sobre_2(n):
    m = Metricas()
    insertion_sort(list(range(n, 0, -1)), metricas=m)
    assert m.comparaciones == n * (n - 1) // 2


def test_es_estable():
    for entrada in arreglos_aleatorios(cantidad=100):
        datos = [Clave(v % 7, i) for i, v in enumerate(entrada)]
        salida = insertion_sort(datos)
        assert all(not (a.clave == b.clave and a.origen > b.origen)
                   for a, b in zip(salida, salida[1:]))
