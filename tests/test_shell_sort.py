"""Pruebas unitarias de Shell Sort (algoritmo propio)."""

from collections import Counter

import pytest

from algoritmos import Metricas
from algoritmos.shell_sort import (SECUENCIAS, gaps_ciura, gaps_knuth,
                                   gaps_shell, shell_sort, shell_sort_traza)
from tests.comun import CASOS_BORDE, Clave, arreglos_aleatorios


@pytest.mark.parametrize("nombre,entrada", CASOS_BORDE)
def test_casos_borde(nombre, entrada):
    assert shell_sort(entrada) == sorted(entrada)


def test_aleatorios_ordenados_y_permutacion():
    for entrada in arreglos_aleatorios():
        salida = shell_sort(entrada)
        assert salida == sorted(entrada)
        assert Counter(salida) == Counter(entrada)


def test_no_modifica_la_entrada():
    entrada = [5, 1, 4, 2, 3]
    shell_sort(entrada)
    assert entrada == [5, 1, 4, 2, 3]


@pytest.mark.parametrize("nombre", list(SECUENCIAS))
def test_todas_las_secuencias_de_gaps_ordenan(nombre):
    for entrada in arreglos_aleatorios(cantidad=60):
        assert shell_sort(entrada, secuencia=SECUENCIAS[nombre]) == sorted(entrada)


@pytest.mark.parametrize("generar", [gaps_shell, gaps_knuth, gaps_ciura])
@pytest.mark.parametrize("n", [2, 3, 10, 100, 5000])
def test_gaps_decrecientes_y_terminan_en_1(generar, n):
    gaps = generar(n)
    assert gaps[-1] == 1
    assert all(a > b for a, b in zip(gaps, gaps[1:]))


def test_gaps_knuth_conocidos():
    assert gaps_knuth(1000) == [364, 121, 40, 13, 4, 1]


def test_mejor_caso_comparaciones_exactas():
    n = 1000
    m = Metricas()
    shell_sort(list(range(n)), metricas=m)
    assert m.comparaciones == sum(n - h for h in gaps_knuth(n))
    assert m.movimientos == 0


def test_cota_peor_caso_n_1_5():
    """Con gaps de Knuth las comparaciones no superan c·n^1.5."""
    for n in (500, 2000):
        m = Metricas()
        shell_sort(list(range(n, 0, -1)), metricas=m)
        assert m.comparaciones <= 2 * n ** 1.5


def test_no_es_estable():
    """Shell Sort NO es estable: con estos datos, dos claves iguales se invierten."""
    datos = [Clave(c, i) for i, c in enumerate([2, 1, 1, 0, 2, 1, 0, 0, 1, 2])]
    salida = shell_sort(datos, secuencia=gaps_shell)
    hay_inversion = any(a.clave == b.clave and a.origen > b.origen
                        for a, b in zip(salida, salida[1:]))
    assert hay_inversion


def test_traza_termina_ordenada_con_gap_1():
    traza = shell_sort_traza([9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
    assert traza[-1][0] == 1
    assert traza[-1][1] == list(range(10))
