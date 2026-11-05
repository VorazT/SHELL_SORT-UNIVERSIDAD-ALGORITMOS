"""
verificador.py
==============

Verificación de CALIDAD DE SOFTWARE de cada algoritmo, por separado.

Un algoritmo de ordenamiento es correcto si, para CUALQUIER entrada:

1. el resultado está ordenado de menor a mayor,
2. el resultado es una permutación de la entrada (no se pierde ni se inventa
   ningún valor),
3. no altera los datos originales (este proyecto trabaja sobre copias),
4. cumple las propiedades que dice su documentación (estabilidad y número de
   comparaciones en el mejor caso).

Cada verificación se ejecuta sobre los tres algoritmos y el resultado se
imprime como tabla y se guarda en ``resultados/calidad/calidad_<algoritmo>.md``.

Además de este verificador, la carpeta ``tests/`` tiene pruebas unitarias con
pytest (una por algoritmo) para correr en VS Code o en GitHub.
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Tuple

from algoritmos import FichaAlgoritmo, Metricas
from algoritmos.shell_sort import gaps_knuth


@dataclass
class Resultado:
    """Resultado de una verificación individual."""

    nombre: str
    aprobada: bool
    detalle: str


@dataclass
class Informe:
    """Todas las verificaciones de un algoritmo."""

    ficha: FichaAlgoritmo
    resultados: List[Resultado] = field(default_factory=list)
    segundos: float = 0.0

    @property
    def aprobadas(self) -> int:
        return sum(r.aprobada for r in self.resultados)

    @property
    def total(self) -> int:
        return len(self.resultados)


class _Clave:
    """Valor que se compara SOLO por ``clave``; ``origen`` guarda su posición
    inicial. Sirve para detectar si un algoritmo es estable."""

    __slots__ = ("clave", "origen")

    def __init__(self, clave: int, origen: int) -> None:
        self.clave = clave
        self.origen = origen

    def __gt__(self, otro: "_Clave") -> bool:
        return self.clave > otro.clave

    def __lt__(self, otro: "_Clave") -> bool:
        return self.clave < otro.clave


# ---------------------------------------------------------------------------
# Comparaciones esperadas en el mejor caso (entrada ya ordenada)
# ---------------------------------------------------------------------------

def _mejor_caso_esperado(clave: str, n: int) -> int:
    """Número EXACTO de comparaciones con una entrada ya ordenada.

    * Insertion: n - 1 (cada elemento se compara solo con su vecino).
    * Shell:     Σ (n - h) para cada gap h de Knuth.
    Heap Sort no tiene fórmula exacta sencilla; se verifica con su cota.
    """
    if clave == "insertion":
        return max(n - 1, 0)
    if clave == "shell":
        return sum(n - h for h in gaps_knuth(n)) if n > 1 else 0
    raise KeyError(clave)


# ---------------------------------------------------------------------------
# Verificaciones
# ---------------------------------------------------------------------------

def _caso(funcion: Callable, entrada: list) -> Tuple[bool, str]:
    salida = funcion(entrada)
    ok = salida == sorted(entrada)
    return ok, f"igual a sorted() (n={len(entrada)})" if ok \
        else f"esperado {sorted(entrada)[:6]}, obtenido {salida[:6]}"


def verificar(ficha: FichaAlgoritmo, aleatorios: int = 1000,
              semilla: int = 7) -> Informe:
    """Ejecuta todas las verificaciones de calidad sobre un algoritmo.

    Args:
        ficha:      algoritmo a verificar.
        aleatorios: cuántos arreglos aleatorios se prueban contra ``sorted``.
        semilla:    semilla para que la verificación sea reproducible.

    Returns:
        Un :class:`Informe` con el resultado de cada verificación.
    """
    rng = random.Random(semilla)
    f = ficha.funcion
    informe = Informe(ficha)
    agregar = informe.resultados.append
    inicio = time.perf_counter()

    # 1-7. Casos borde --------------------------------------------------------
    casos_borde = [
        ("Arreglo vacío", []),
        ("Un solo elemento", [42]),
        ("Dos elementos desordenados", [2, 1]),
        ("Ya ordenado (mejor caso)", list(range(1, 21))),
        ("Orden inverso", list(range(20, 0, -1))),
        ("Con valores repetidos", [5, 3, 5, 1, 3, 5, 1]),
        ("Todos iguales", [7] * 15),
        ("Negativos y decimales", [3.5, -2, 0, -7.25, 10, 1e-3]),
        ("Cadenas de texto", ["pera", "uva", "kiwi", "banano", "anón"]),
    ]
    for nombre, entrada in casos_borde:
        ok, detalle = _caso(f, entrada)
        agregar(Resultado(nombre, ok, detalle))

    # 8. No modifica la entrada ---------------------------------------------
    original = [rng.randint(0, 99) for _ in range(50)]
    copia = list(original)
    f(original)
    agregar(Resultado("No modifica la entrada", original == copia,
                      "lista original intacta" if original == copia
                      else "¡la lista original cambió!"))

    # 9. Funciona con tuplas (cualquier secuencia) ----------------------------
    tupla = (9, 4, 7, 1)
    ok = f(tupla) == [1, 4, 7, 9]
    agregar(Resultado("Acepta cualquier secuencia (tupla)", ok,
                      "(9, 4, 7, 1) → [1, 4, 7, 9]" if ok else "falló"))

    # 10-11. Prueba masiva aleatoria: ordenado + permutación ----------------
    fallos_orden = fallos_perm = 0
    for _ in range(aleatorios):
        n = rng.randint(0, 200)
        entrada = [rng.randint(-1000, 1000) for _ in range(n)]
        salida = f(entrada)
        if any(salida[i] > salida[i + 1] for i in range(len(salida) - 1)):
            fallos_orden += 1
        if Counter(salida) != Counter(entrada):
            fallos_perm += 1
    agregar(Resultado(f"{aleatorios} arreglos aleatorios quedan ordenados",
                      fallos_orden == 0, f"{fallos_orden} fallos"))
    agregar(Resultado("Salida es permutación de la entrada",
                      fallos_perm == 0,
                      f"{fallos_perm} valores perdidos o inventados"))

    # 12. Contar operaciones no altera el resultado ---------------------------
    entrada = [rng.randint(0, 500) for _ in range(300)]
    ok = f(entrada) == f(entrada, metricas=Metricas())
    agregar(Resultado("Métricas no alteran el resultado", ok,
                      "mismo resultado con contador" if ok else "difieren"))

    # 13. El conteo de comparaciones respeta la teoría ------------------------
    errores = []
    if ficha.clave == "heap":
        # Heap Sort: como máximo 2·n·log₂n comparaciones en cualquier entrada.
        for n in (10, 100, 1000):
            for entrada in (list(range(n)), list(range(n, 0, -1)),
                            [rng.randint(0, n) for _ in range(n)]):
                m = Metricas()
                f(entrada, metricas=m)
                cota = 2 * n * math.log2(n)
                if m.comparaciones > cota:
                    errores.append(f"n={n}: {m.comparaciones}>{cota:.0f}")
        agregar(Resultado("Comparaciones ≤ 2·n·log₂n (cota)", not errores,
                          "se cumple en n = 10 … 1000, 3 tipos de entrada"
                          if not errores else "; ".join(errores)))
    else:
        for n in (1, 2, 10, 100, 1000):
            m = Metricas()
            f(list(range(n)), metricas=m)
            esperado = _mejor_caso_esperado(ficha.clave, n)
            if m.comparaciones != esperado:
                errores.append(f"n={n}: {m.comparaciones}≠{esperado}")
        agregar(Resultado("Mejor caso: comparaciones = fórmula", not errores,
                          "exacto en n = 1 … 1000" if not errores
                          else "; ".join(errores)))

    # 14. Estabilidad coincide con lo documentado -----------------------------
    inestable = False
    for _ in range(200):
        claves = [rng.randint(0, 5) for _ in range(30)]
        salida = f([_Clave(c, i) for i, c in enumerate(claves)])
        if any(a.clave == b.clave and a.origen > b.origen
               for a, b in zip(salida, salida[1:])):
            inestable = True
            break
    estable_observado = not inestable
    ok = estable_observado == ficha.estable
    texto = "estable" if estable_observado else "no estable"
    agregar(Resultado("Estabilidad coincide con la documentación", ok,
                      f"observado = documentado ({texto})" if ok else
                      f"observado {texto}, documentado lo contrario"))

    informe.segundos = time.perf_counter() - inicio
    return informe


# ---------------------------------------------------------------------------
# Presentación del informe
# ---------------------------------------------------------------------------

def imprimir(informe: Informe) -> None:
    """Muestra el informe como tabla en la consola."""
    ficha = informe.ficha
    print(f"\n  ■ {ficha.nombre}  —  {informe.aprobadas}/{informe.total} "
          f"verificaciones aprobadas  ({informe.segundos:.2f} s)")
    print("  " + "─" * 76)
    for r in informe.resultados:
        marca = "✔" if r.aprobada else "✘"
        print(f"   {marca}  {r.nombre:<43} {r.detalle}")


def guardar_markdown(informe: Informe, carpeta: Path) -> Path:
    """Guarda el informe en Markdown (se ve como tabla en GitHub)."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ficha = informe.ficha
    lineas = [
        f"# Calidad de software — {ficha.nombre}",
        "",
        f"**Resultado:** {informe.aprobadas}/{informe.total} verificaciones "
        f"aprobadas en {informe.segundos:.2f} s",
        "",
        f"Complejidad documentada: mejor {ficha.mejor} · promedio "
        f"{ficha.promedio} · peor {ficha.peor} · "
        f"{'estable' if ficha.estable else 'no estable'} · in-place O(1)",
        "",
        "| # | Verificación | Estado | Detalle |",
        "|---|---|---|---|",
    ]
    for i, r in enumerate(informe.resultados, 1):
        detalle = r.detalle.replace("|", "\\|")
        lineas.append(f"| {i} | {r.nombre} | {'✅' if r.aprobada else '❌'} "
                      f"| {detalle} |")
    ruta = carpeta / f"calidad_{ficha.clave}.md"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta
