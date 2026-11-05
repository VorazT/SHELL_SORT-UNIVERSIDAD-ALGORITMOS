"""
main.py — Producto didáctico y comparativo de ordenamiento
==========================================================

Algoritmo propio: **Shell Sort**. Se compara con **Insertion Sort** (su base:
Shell Sort con gap = 1) y **Heap Sort** (mismo perfil: in-place y no estable,
pero con Θ(n log n) garantizado).

Uso (desde la terminal de VS Code, en la carpeta del proyecto)::

    python main.py                 # menú interactivo
    python main.py demo            # Shell Sort paso a paso con tus valores
    python main.py calidad         # verificación de calidad de cada algoritmo
    python main.py graficas        # mediciones + todas las gráficas
    python main.py todo            # calidad + gráficas
    python main.py graficas --rapido        # versión corta (para probar)
    python main.py graficas --n-max 10000   # cambia el rango de arreglos

Todo lo que se genera queda en la carpeta ``resultados/``.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List

from algoritmos import ALGORITMOS, Metricas
from algoritmos.shell_sort import gaps_knuth, shell_sort_traza
from analisis import benchmark, graficas
from analisis.generadores import tamanos
from calidad import verificador

RAIZ = Path(__file__).resolve().parent
RESULTADOS = RAIZ / "resultados"
CARPETA_GRAFICAS = RESULTADOS / "graficas"
CARPETA_DATOS = RESULTADOS / "datos"
CARPETA_CALIDAD = RESULTADOS / "calidad"

if hasattr(sys.stdout, "reconfigure"):          # tildes y símbolos en Windows
    sys.stdout.reconfigure(encoding="utf-8")


def _titulo(texto: str) -> None:
    print("\n" + "═" * 78)
    print(f"  {texto}")
    print("═" * 78)


# ---------------------------------------------------------------------------
# 1. Demo paso a paso
# ---------------------------------------------------------------------------

def _barras(arreglo: List[float], ancho: int = 30) -> str:
    """Representa cada valor como una barra de texto (para la demo)."""
    maximo = max(abs(v) for v in arreglo) or 1
    return "\n".join(f"      {v:>6g} │{'█' * max(1, round(abs(v) / maximo * ancho))}"
                     for v in arreglo)


def _leer_valores(texto: str) -> List[float]:
    """Convierte '5, 3 8,1' en [5, 3, 8, 1]. Acepta comas o espacios."""
    partes = texto.replace(",", " ").split()
    return [float(p) if "." in p else int(p) for p in partes]


def demo(valores: List[float] | None = None) -> None:
    """Muestra Shell Sort paso a paso y compara las operaciones de los tres."""
    _titulo("DEMO — Shell Sort paso a paso (gaps de Knuth: 1, 4, 13, 40, ...)")
    if valores is None:
        texto = input("  Escribe números separados por comas o espacios\n"
                      "  (Enter = ejemplo 35 33 42 10 14 19 27 44 26 31): ")
        try:
            valores = _leer_valores(texto) if texto.strip() else \
                [35, 33, 42, 10, 14, 19, 27, 44, 26, 31]
        except ValueError:
            print("  ⚠ Valores no válidos; se usa el ejemplo.")
            valores = [35, 33, 42, 10, 14, 19, 27, 44, 26, 31]

    print(f"\n  Entrada (n = {len(valores)}): {valores}")
    print(_barras(valores))
    print(f"\n  Gaps que se usarán: {gaps_knuth(len(valores))}")
    for gap, estado in shell_sort_traza(valores):
        print(f"\n  ▸ Después de ordenar con gap = {gap}: {estado}")
        print(_barras(estado))

    print("\n  Operaciones de cada algoritmo con estos mismos datos:")
    print(f"  {'Algoritmo':<16}{'Comparaciones':>15}{'Movimientos':>14}"
          f"{'Pasadas':>10}")
    for ficha in ALGORITMOS:
        m = Metricas()
        ficha.funcion(valores, metricas=m)
        print(f"  {ficha.nombre:<16}{m.comparaciones:>15,}{m.movimientos:>14,}"
              f"{m.pasadas:>10}")


# ---------------------------------------------------------------------------
# 2. Calidad de software
# ---------------------------------------------------------------------------

def calidad() -> bool:
    """Verifica cada algoritmo por separado. Retorna True si todo aprobó."""
    _titulo("CALIDAD DE SOFTWARE — verificación de cada algoritmo por separado")
    todo_ok = True
    for ficha in ALGORITMOS:
        informe = verificador.verificar(ficha)
        verificador.imprimir(informe)
        ruta = verificador.guardar_markdown(informe, CARPETA_CALIDAD)
        print(f"     informe → {ruta.relative_to(RAIZ)}")
        todo_ok &= informe.aprobadas == informe.total
    print("\n  Resultado general:", "✔ TODO APROBADO" if todo_ok
          else "✘ HAY VERIFICACIONES FALLIDAS")
    return todo_ok


# ---------------------------------------------------------------------------
# 3. Mediciones y gráficas
# ---------------------------------------------------------------------------

def graficas_y_mediciones(n_max: int = 5000, puntos: int = 10,
                          n_ampliado: int = 50000,
                          limite_cuadratico: int = 8000) -> None:
    """Mide los tres algoritmos con un rango creciente de tamaños y grafica.

    Args:
        n_max:             tamaño máximo para el análisis de cada algoritmo.
        puntos:            cuántos tamaños medir entre n_max/puntos y n_max.
        n_ampliado:        tamaño máximo del "rango ampliado" (Shell y Heap).
        limite_cuadratico: hasta qué n se mide Insertion Sort en el rango
                           ampliado (por ser O(n²) tardaría demasiado).
    """
    _titulo("MEDICIONES Y GRÁFICAS — rango de arreglos creciente")
    inicio = time.perf_counter()
    ns = tamanos(max(n_max // puntos, 10), n_max, puntos)
    print(f"  Tamaños: {ns[0]:,} → {ns[-1]:,} ({len(ns)} tamaños)")

    print("  · Funciones teóricas f(n)")
    graficas.grafica_funciones_teoricas(CARPETA_GRAFICAS)

    tiempos_todos, operaciones_aleatorio = {}, {}
    for ficha in ALGORITMOS:
        print(f"  · {ficha.nombre}: contando comparaciones y midiendo tiempo...")
        ops = benchmark.contar_operaciones(ficha, ns)
        tiempos = benchmark.medir_tiempo(ficha.funcion, ns)
        resumen = graficas.grafica_algoritmo(ficha, ns, ops, tiempos,
                                             CARPETA_GRAFICAS)
        benchmark.guardar_csv(CARPETA_DATOS / f"{ficha.clave}_comparaciones.csv",
                              ns, ops)
        tiempos_todos[ficha.clave] = tiempos
        operaciones_aleatorio[ficha.clave] = ops["aleatorio"]
        for caso, datos in resumen.items():
            ajuste = f"{datos['c']:.4g}·{datos['modelo']}"
            print(f"      {caso:<10} ≈ {ajuste:<24} R² = {datos['r2']:.4f}")

    benchmark.guardar_csv(CARPETA_DATOS / "tiempos_ms.csv", ns, tiempos_todos)
    print("  · Comparación de los tres algoritmos")
    graficas.grafica_comparacion(
        ALGORITMOS, ns, tiempos_todos, CARPETA_GRAFICAS,
        "comparacion_tiempo.png",
        "Tiempo de ejecución — entrada aleatoria", "tiempo (ms)",
        nota="mediana de 5 ejecuciones por tamaño")
    graficas.grafica_comparacion(
        ALGORITMOS, ns, operaciones_aleatorio, CARPETA_GRAFICAS,
        "comparacion_operaciones.png",
        "Comparaciones — entrada aleatoria (escala logarítmica)",
        "comparaciones (log)", log=True,
        nota="cada línea de la rejilla = 10 veces más operaciones")

    print(f"  · Rango ampliado hasta n = {n_ampliado:,}")
    ns_amp = tamanos(n_ampliado // 20, n_ampliado, 20)
    tiempos_amp = {}
    for ficha in ALGORITMOS:
        ns_validos = [n for n in ns_amp
                      if ficha.clave != "insertion" or n <= limite_cuadratico]
        tiempos_amp[ficha.clave] = benchmark.medir_tiempo(
            ficha.funcion, ns_validos, repeticiones=1)
    benchmark.guardar_csv(CARPETA_DATOS / "tiempos_rango_ampliado_ms.csv",
                          ns_amp, tiempos_amp)
    graficas.grafica_comparacion(
        ALGORITMOS, ns_amp, tiempos_amp, CARPETA_GRAFICAS,
        "rango_ampliado.png",
        f"Rango ampliado: arreglos de hasta {n_ampliado:,} elementos".replace(",", "."),
        "tiempo (ms, escala logarítmica)", log=True,
        nota=f"Insertion Sort solo se mide hasta n = {limite_cuadratico:,} "
             "por ser O(n²)".replace(",", "."))

    print("  · Shell Sort con distintas secuencias de gaps")
    gaps = benchmark.comparar_secuencias_gaps(ns)
    benchmark.guardar_csv(CARPETA_DATOS / "shell_secuencias_gaps.csv", ns, gaps)
    graficas.grafica_secuencias_gaps(ns, gaps, CARPETA_GRAFICAS)

    print(f"\n  ✔ Listo en {time.perf_counter() - inicio:.1f} s → "
          f"{CARPETA_GRAFICAS.relative_to(RAIZ)}")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def _menu() -> None:
    opciones = {
        "1": ("Demo de Shell Sort paso a paso", demo),
        "2": ("Verificar la calidad de los 3 algoritmos", calidad),
        "3": ("Medir y generar las gráficas", graficas_y_mediciones),
        "4": ("Todo (calidad + gráficas)", lambda: (calidad(),
                                                     graficas_y_mediciones())),
    }
    while True:
        _titulo("ANÁLISIS DE ALGORITMOS — Shell Sort vs Insertion Sort vs Heap Sort")
        for clave, (texto, _) in opciones.items():
            print(f"   {clave}. {texto}")
        print("   0. Salir")
        eleccion = input("\n  Opción: ").strip()
        if eleccion == "0":
            break
        if eleccion in opciones:
            opciones[eleccion][1]()
            input("\n  Enter para volver al menú...")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Producto didáctico y comparativo de ordenamiento.")
    parser.add_argument("accion", nargs="?",
                        choices=["demo", "calidad", "graficas", "todo"])
    parser.add_argument("--valores", help="valores para la demo, ej. '5,3,8,1'")
    parser.add_argument("--n-max", type=int, default=5000,
                        help="tamaño máximo de arreglo (por defecto 5000)")
    parser.add_argument("--n-ampliado", type=int, default=50000,
                        help="tamaño máximo del rango ampliado (50000)")
    parser.add_argument("--rapido", action="store_true",
                        help="mediciones cortas para probar que todo funciona")
    args = parser.parse_args(argv)

    if args.rapido:
        args.n_max, args.n_ampliado = 600, 3000
    parametros = dict(n_max=args.n_max, n_ampliado=args.n_ampliado,
                      limite_cuadratico=min(8000, args.n_ampliado))

    if args.accion is None:
        _menu()
    elif args.accion == "demo":
        demo(_leer_valores(args.valores) if args.valores else None)
    elif args.accion == "calidad":
        return 0 if calidad() else 1
    elif args.accion == "graficas":
        graficas_y_mediciones(**parametros)
    elif args.accion == "todo":
        ok = calidad()
        graficas_y_mediciones(**parametros)
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
