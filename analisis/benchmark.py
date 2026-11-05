"""
benchmark.py
============

Mide cada algoritmo sobre arreglos de tamaño creciente.

Se toman dos medidas:

1. **Operaciones** (comparaciones): se cuentan con :class:`Metricas`. Son
   exactas y no dependen del computador → se comparan con f(n).
2. **Tiempo** (milisegundos): se mide con ``time.perf_counter_ns``, se repite
   varias veces y se toma la MEDIANA para que un pico del sistema operativo no
   dañe el resultado. Durante la medición se apaga el recolector de basura.

Los resultados se guardan también en CSV (carpeta ``resultados/datos``) para
poder revisarlos en Excel.
"""

from __future__ import annotations

import csv
import gc
import statistics
import time
from pathlib import Path
from typing import Callable, Dict, List, Sequence

from algoritmos import FichaAlgoritmo, Metricas, shell_sort
from algoritmos.shell_sort import SECUENCIAS

from .generadores import TIPOS, aleatorio

Serie = Dict[str, List[float]]   # nombre de la serie → valores por tamaño


def contar_operaciones(ficha: FichaAlgoritmo, ns: Sequence[int]) -> Serie:
    """Cuenta las comparaciones de un algoritmo en los tres tipos de entrada.

    Args:
        ficha: algoritmo a medir.
        ns:    tamaños de arreglo.

    Returns:
        ``{"aleatorio": [...], "ordenado": [...], "inverso": [...]}`` con el
        número de comparaciones para cada tamaño.
    """
    resultado: Serie = {}
    for tipo, generar in TIPOS.items():
        valores = []
        for n in ns:
            metricas = Metricas()
            ficha.funcion(generar(n), metricas=metricas)
            valores.append(metricas.comparaciones)
        resultado[tipo] = valores
    return resultado


def medir_tiempo(funcion: Callable[[List[int]], List[int]],
                 ns: Sequence[int],
                 generar: Callable[[int], List[int]] = aleatorio,
                 repeticiones: int = 5) -> List[float]:
    """Tiempo de ejecución (mediana, en milisegundos) para cada tamaño.

    Args:
        funcion:      algoritmo de ordenamiento (sin métricas, para no sumar
                      costo extra a la medición).
        ns:           tamaños de arreglo.
        generar:      generador de la entrada (por defecto, aleatorio).
        repeticiones: cuántas veces se mide cada tamaño.

    Returns:
        Lista con la mediana del tiempo, en ms, para cada tamaño.
    """
    tiempos = []
    for n in ns:
        datos = generar(n)
        muestras = []
        gc_activo = gc.isenabled()
        gc.disable()
        try:
            for _ in range(repeticiones):
                inicio = time.perf_counter_ns()
                funcion(datos)
                muestras.append(time.perf_counter_ns() - inicio)
        finally:
            if gc_activo:
                gc.enable()
        tiempos.append(statistics.median(muestras) / 1e6)
    return tiempos


def comparar_secuencias_gaps(ns: Sequence[int]) -> Serie:
    """Comparaciones de Shell Sort (entrada aleatoria) con cada secuencia de gaps."""
    resultado: Serie = {}
    for nombre, secuencia in SECUENCIAS.items():
        valores = []
        for n in ns:
            metricas = Metricas()
            shell_sort(aleatorio(n), secuencia=secuencia, metricas=metricas)
            valores.append(metricas.comparaciones)
        resultado[nombre] = valores
    return resultado


def guardar_csv(ruta: Path, ns: Sequence[int], series: Serie) -> None:
    """Guarda una tabla ``n, serie1, serie2, ...`` en CSV (separador ;)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(["n", *series.keys()])
        for i, n in enumerate(ns):
            fila = [series[s][i] if i < len(series[s]) else "" for s in series]
            escritor.writerow([n, *fila])
