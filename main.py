"""
main.py — Producto didáctico y comparativo de ordenamiento
==========================================================

Algoritmo propio: **Shell Sort**. Se compara con **Insertion Sort** (su base:
Shell Sort con gap = 1) y **Heap Sort** (mismo perfil: in-place y no estable,
pero con Θ(n log n) garantizado).

Cómo usarlo (terminal de VS Code, dentro de la carpeta del proyecto)::

    python main.py            # menú (recomendado)

También se puede llamar cada parte directamente::

    python main.py demo --valores "35 33 42 10 14 19 27 44"
    python main.py calidad
    python main.py graficas               # datos aleatorios, hasta n = 5.000
    python main.py graficas --n-max 3000 --sin-ventana

Todo lo que se genera queda en la carpeta ``resultados/``.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from algoritmos import ALGORITMOS, Metricas
from algoritmos.shell_sort import gaps_knuth, shell_sort_traza
from analisis import benchmark, graficas, visor
from analisis.generadores import (aleatorio_con_semilla, desde_patron,
                                  tamanos, tipos_de_entrada)
from calidad import verificador

RAIZ = Path(__file__).resolve().parent
RESULTADOS = RAIZ / "resultados"
CARPETA_GRAFICAS = RESULTADOS / "graficas"
CARPETA_DATOS = RESULTADOS / "datos"
CARPETA_CALIDAD = RESULTADOS / "calidad"

# Límites que se le explican al usuario.
DEMO_MIN, DEMO_MAX, DEMO_DEFECTO = 5, 20, 12        # números para la demo
PATRON_MIN, PATRON_MAX = 10, 100                    # números para las gráficas
N_MIN, N_MAX, N_DEFECTO = 500, 8000, 5000           # tamaño máximo a medir

if hasattr(sys.stdout, "reconfigure"):              # tildes y símbolos en Windows
    sys.stdout.reconfigure(encoding="utf-8")


# ===========================================================================
# Utilidades de la terminal
# ===========================================================================

def limpiar() -> None:
    """Borra la pantalla de la terminal (Windows, Linux o macOS)."""
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def encabezado(titulo: str, explicacion: str = "") -> None:
    """Limpia la pantalla y muestra un título con una explicación corta."""
    limpiar()
    print("═" * 72)
    print(f"  {titulo}")
    print("═" * 72)
    if explicacion:
        print(f"\n  {explicacion}\n")


def pausa(texto: str = "Pulsa Enter para volver al menú...") -> None:
    input(f"\n  {texto}")


def pedir_opcion(pregunta: str, opciones: Dict[str, str]) -> str:
    """Muestra opciones numeradas y repite hasta que la respuesta sea válida."""
    print(f"  {pregunta}")
    for clave, texto in opciones.items():
        print(f"    {clave}. {texto}")
    while True:
        respuesta = input("\n  Escribe el número de la opción: ").strip()
        if respuesta in opciones:
            return respuesta
        print(f"  ⚠ Escribe solo {', '.join(opciones)}.")


def pedir_entero(pregunta: str, minimo: int, maximo: int, defecto: int) -> int:
    """Pide un número entero dentro de un rango. Enter = valor por defecto."""
    while True:
        texto = input(f"  {pregunta} [entre {minimo:,} y {maximo:,}, "
                      f"Enter = {defecto:,}]: ".replace(",", ".")).strip()
        if not texto:
            return defecto
        try:
            valor = int(texto.replace(".", "").replace(",", ""))
        except ValueError:
            print("  ⚠ Escribe un número entero, por ejemplo 3000.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"  ⚠ Debe estar entre {minimo:,} y {maximo:,}.".replace(",", "."))


def leer_numeros(texto: str) -> List[float]:
    """Convierte '5, 3 8,1' en [5, 3, 8, 1]. Acepta comas o espacios."""
    return [float(p) if "." in p else int(p)
            for p in texto.replace(",", " ").split()]


def pedir_numeros(minimo: int, maximo: int, ejemplo: str) -> List[float]:
    """Pide al usuario entre ``minimo`` y ``maximo`` números."""
    print(f"  Escribe entre {minimo} y {maximo} números separados por espacios "
          f"o comas.\n  Ejemplo: {ejemplo}\n")
    while True:
        try:
            valores = leer_numeros(input("  Tus números: "))
        except ValueError:
            print("  ⚠ Solo números (puedes usar negativos y decimales con punto).")
            continue
        if minimo <= len(valores) <= maximo:
            return valores
        print(f"  ⚠ Escribiste {len(valores)}; deben ser entre {minimo} y {maximo}.")


def barra_progreso(paso: int, total: int, texto: str) -> None:
    """Dibuja una sola línea de progreso que se va actualizando."""
    lleno = round(paso / total * 30)
    print(f"\r  [{'█' * lleno}{'░' * (30 - lleno)}] {paso * 100 // total:3d}%  "
          f"{texto:<42}", end="", flush=True)


# ===========================================================================
# 1. Shell Sort paso a paso
# ===========================================================================

def _barras(arreglo: List[float], ancho: int = 32) -> str:
    """Cada valor como una barra de texto, para ver cómo se mueven."""
    maximo = max(abs(v) for v in arreglo) or 1
    return "\n".join(
        f"     {v:>7g} │{'█' * max(1, round(abs(v) / maximo * ancho))}"
        for v in arreglo)


def demo(valores: Optional[List[float]] = None) -> None:
    """Muestra cómo Shell Sort ordena unos pocos números, gap por gap."""
    encabezado("SHELL SORT PASO A PASO",
               "Mira cómo Shell Sort ordena comparando números que están LEJOS\n"
               "  (separados por un 'gap') y luego cada vez más cerca, hasta gap = 1.")
    if valores is None:
        origen = pedir_opcion("¿Qué números quieres ordenar?", {
            "1": "Números aleatorios (los crea el programa)",
            "2": "Quiero escribir mis números"})
        print()
        if origen == "1":
            cantidad = pedir_entero("¿Cuántos números?", DEMO_MIN, DEMO_MAX,
                                    DEMO_DEFECTO)
            valores = [random.randint(1, 99) for _ in range(cantidad)]
        else:
            valores = pedir_numeros(DEMO_MIN, DEMO_MAX,
                                    "35 33 42 10 14 19 27 44 26 31")

    gaps = gaps_knuth(len(valores))
    encabezado("SHELL SORT PASO A PASO")
    print(f"  Números a ordenar ({len(valores)}): {valores}")
    print(f"  Gaps que se usarán (Knuth): {gaps}\n")
    print("  ▸ ANTES de ordenar")
    print(_barras(valores))
    for gap, estado in shell_sort_traza(valores):
        input(f"\n  Pulsa Enter para ordenar con gap = {gap}...")
        if gap > 1:
            print(f"  ▸ Gap = {gap}: se comparan los números separados "
                  f"{gap} posiciones")
        else:
            print("  ▸ Gap = 1: último repaso (Insertion Sort normal) "
                  "sobre datos casi ordenados")
        print(_barras(estado))

    print("\n  ✔ ¡Ordenado! Cuántas operaciones necesitó cada algoritmo "
          "con estos mismos números:\n")
    print(f"     {'Algoritmo':<16}{'Comparaciones':>15}{'Movimientos':>14}")
    print("     " + "─" * 45)
    resultados = []
    for ficha in ALGORITMOS:
        m = Metricas()
        ficha.funcion(valores, metricas=m)
        resultados.append((m.comparaciones, ficha.nombre))
        print(f"     {ficha.nombre:<16}{m.comparaciones:>15,}{m.movimientos:>14,}")
    menos = min(resultados)[1]
    print(f"\n  El que menos comparó fue: {menos}.")
    print("  (Con tan pocos números la diferencia es pequeña; la opción 3 "
          "mide con miles.)")
    pausa()


# ===========================================================================
# 2. Calidad de software
# ===========================================================================

def calidad(esperar: bool = True) -> bool:
    """Verifica cada algoritmo por separado. Retorna True si todo aprobó."""
    encabezado("CALIDAD DE SOFTWARE",
               "Cada algoritmo se prueba POR SEPARADO con 16 verificaciones:\n"
               "  casos borde, 1.000 arreglos aleatorios, que no pierda valores,\n"
               "  que no cambie los datos originales y que cumpla su teoría.")
    todo_ok = True
    for ficha in ALGORITMOS:
        print(f"  Verificando {ficha.nombre}...", end="\r", flush=True)
        informe = verificador.verificar(ficha)
        verificador.guardar_markdown(informe, CARPETA_CALIDAD)
        ok = informe.aprobadas == informe.total
        todo_ok &= ok
        print(f"  {'✔' if ok else '✘'} {ficha.nombre:<16} "
              f"{informe.aprobadas}/{informe.total} verificaciones aprobadas")
        for r in informe.resultados:
            if not r.aprobada:
                print(f"      ✘ {r.nombre}: {r.detalle}")

    print("\n  Lo que se verificó en cada uno:")
    nombres = [r.nombre for r in informe.resultados]
    mitad = (len(nombres) + 1) // 2
    for izquierda, derecha in zip(nombres[:mitad], nombres[mitad:] + [""]):
        print(f"    · {izquierda:<38}{'· ' + derecha if derecha else ''}")

    print(f"\n  Resultado: {'✔ TODO APROBADO' if todo_ok else '✘ HAY FALLAS'}")
    print(f"  Informe detallado de cada algoritmo en: "
          f"{CARPETA_CALIDAD.relative_to(RAIZ)}")
    if esperar:
        pausa()
    return todo_ok


# ===========================================================================
# 3. Medir y ver las gráficas
# ===========================================================================

def medir_y_graficar(generar: Callable[[int], List[float]], caso: str,
                     entrada: str, n_max: int = N_DEFECTO) -> float:
    """Mide los tres algoritmos con arreglos cada vez más grandes y grafica.

    Args:
        generar: crea el arreglo principal de tamaño n (aleatorio o tus datos).
        caso:    nombre de ese caso en las gráficas ("aleatorio"/"tus datos").
        entrada: texto para los títulos ("aleatoria"/"con tus datos").
        n_max:   tamaño más grande a medir.

    Returns:
        Segundos que tardó todo el cálculo.
    """
    inicio = time.perf_counter()
    ns = tamanos(n_max // 10, n_max, 10)
    n_ampliado = min(n_max * 10, 50_000)
    limite_cuadratico = min(int(n_max * 1.6), 8000)
    repeticiones = 5 if n_max <= 5000 else 3
    tipos = tipos_de_entrada(generar, caso)
    total, paso = 9, 0

    def avance(texto: str) -> None:
        nonlocal paso
        barra_progreso(paso, total, texto)
        paso += 1

    avance("Funciones teóricas f(n)")
    graficas.grafica_funciones_teoricas(CARPETA_GRAFICAS)

    tiempos_todos, operaciones = {}, {}
    for ficha in ALGORITMOS:
        avance(f"Midiendo {ficha.nombre}")
        ops = benchmark.contar_operaciones(ficha, ns, tipos)
        tiempos = benchmark.medir_tiempo(ficha.funcion, ns, generar, repeticiones)
        graficas.grafica_algoritmo(ficha, ns, ops, tiempos, CARPETA_GRAFICAS,
                                   entrada)
        benchmark.guardar_csv(
            CARPETA_DATOS / f"{ficha.clave}_comparaciones.csv", ns, ops)
        tiempos_todos[ficha.clave] = tiempos
        operaciones[ficha.clave] = ops[caso]

    avance("Comparando los tres")
    benchmark.guardar_csv(CARPETA_DATOS / "tiempos_ms.csv", ns, tiempos_todos)
    graficas.grafica_comparacion(
        ALGORITMOS, ns, tiempos_todos, CARPETA_GRAFICAS,
        "comparacion_tiempo.png", f"Tiempo de ejecución — entrada {entrada}",
        "tiempo (ms)", nota=f"mediana de {repeticiones} ejecuciones por tamaño")
    graficas.grafica_comparacion(
        ALGORITMOS, ns, operaciones, CARPETA_GRAFICAS,
        "comparacion_operaciones.png",
        f"Comparaciones — entrada {entrada} (escala logarítmica)",
        "comparaciones (log)", log=True,
        nota="cada línea de la rejilla = 10 veces más operaciones")

    ns_amp = tamanos(n_ampliado // 20, n_ampliado, 20)
    tiempos_amp = {}
    for ficha in ALGORITMOS:
        avance(f"Rango ampliado: {ficha.nombre}")
        validos = [n for n in ns_amp
                   if ficha.clave != "insertion" or n <= limite_cuadratico]
        tiempos_amp[ficha.clave] = benchmark.medir_tiempo(
            ficha.funcion, validos, generar, repeticiones=1)
    benchmark.guardar_csv(CARPETA_DATOS / "tiempos_rango_ampliado_ms.csv",
                          ns_amp, tiempos_amp)
    miles = lambda n: f"{n:,}".replace(",", ".")          # noqa: E731
    graficas.grafica_comparacion(
        ALGORITMOS, ns_amp, tiempos_amp, CARPETA_GRAFICAS, "rango_ampliado.png",
        f"Rango ampliado: arreglos de hasta {miles(n_ampliado)} elementos",
        "tiempo (ms, escala logarítmica)", log=True,
        nota=f"Insertion Sort solo se mide hasta n = {miles(limite_cuadratico)} "
             "por ser O(n²)")

    avance("Secuencias de gaps de Shell Sort")
    gaps = benchmark.comparar_secuencias_gaps(ns, generar)
    benchmark.guardar_csv(CARPETA_DATOS / "shell_secuencias_gaps.csv", ns, gaps)
    graficas.grafica_secuencias_gaps(ns, gaps, CARPETA_GRAFICAS, entrada)

    barra_progreso(total, total, "Listo")
    print()
    return time.perf_counter() - inicio


def opcion_graficas() -> None:
    """Pregunta de dónde salen los datos, mide todo y abre las gráficas."""
    encabezado("MEDIR Y VER LAS GRÁFICAS",
               "El programa ordena arreglos cada vez más grandes con los tres\n"
               "  algoritmos, cuenta comparaciones y mide el tiempo. Luego dibuja\n"
               "  lo medido junto a la curva teórica f(n) de Big O.")
    origen = pedir_opcion("¿Con qué datos quieres medir?", {
        "1": "Números aleatorios (recomendado)",
        "2": "Quiero escribir mis números"})
    print()
    if origen == "1":
        generar = aleatorio_con_semilla(random.randint(1, 1_000_000))
        caso, entrada = "aleatorio", "aleatoria"
    else:
        print(f"  Con tus números se forma un PATRÓN que se repite hasta llenar\n"
              f"  arreglos grandes (por ejemplo [5, 2, 9] → 5 2 9 5 2 9 5 ...).\n"
              f"  Así se puede ver cómo crece el tiempo con tus propios datos.\n")
        patron = pedir_numeros(PATRON_MIN, PATRON_MAX,
                               "35 33 42 10 14 19 27 44 26 31 8 50")
        generar = desde_patron(patron)
        caso, entrada = "tus datos", "con tus datos"

    print("\n  ¿Hasta qué tamaño de arreglo medir? Más grande = curvas más\n"
          "  claras, pero tarda más (Insertion Sort es O(n²)). Con 5.000\n"
          "  tarda alrededor de medio minuto.\n")
    n_max = pedir_entero("Tamaño máximo", N_MIN, N_MAX, N_DEFECTO)

    encabezado("MEDIR Y VER LAS GRÁFICAS",
               f"Midiendo arreglos de {n_max // 10:,} a {n_max:,} elementos "
               f"(entrada {entrada})...".replace(",", "."))
    segundos = medir_y_graficar(generar, caso, entrada, n_max)
    print(f"\n  ✔ Cálculo terminado en {segundos:.0f} segundos. Las gráficas "
          f"quedaron guardadas en {CARPETA_GRAFICAS.relative_to(RAIZ)}")
    if not visor.mostrar(CARPETA_GRAFICAS):
        pausa()


def opcion_ver_graficas() -> None:
    encabezado("VER LAS ÚLTIMAS GRÁFICAS")
    if not visor.mostrar(CARPETA_GRAFICAS):
        pausa()


# ===========================================================================
# Menú principal
# ===========================================================================

def menu() -> None:
    opciones = {
        "1": ("Ver Shell Sort paso a paso", demo),
        "2": ("Verificar la calidad de los 3 algoritmos", calidad),
        "3": ("Medir y ver las gráficas", opcion_graficas),
        "4": ("Volver a abrir las últimas gráficas", opcion_ver_graficas),
    }
    while True:
        encabezado("ANÁLISIS DE ALGORITMOS DE ORDENAMIENTO\n"
                   "  Shell Sort  vs  Insertion Sort  vs  Heap Sort")
        for clave, (texto, _) in opciones.items():
            print(f"    {clave}. {texto}")
        print("    0. Salir\n")
        eleccion = input("  Escribe el número de la opción: ").strip()
        if eleccion == "0":
            limpiar()
            return
        if eleccion in opciones:
            opciones[eleccion][1]()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Producto didáctico y comparativo de ordenamiento.")
    parser.add_argument("accion", nargs="?",
                        choices=["demo", "calidad", "graficas"])
    parser.add_argument("--valores", help="números para la demo, ej. '5,3,8,1'")
    parser.add_argument("--n-max", type=int, default=N_DEFECTO,
                        help=f"tamaño máximo de arreglo (por defecto {N_DEFECTO})")
    parser.add_argument("--sin-ventana", action="store_true",
                        help="solo guarda las gráficas, sin abrir la ventana")
    args = parser.parse_args(argv)

    try:
        if args.accion is None:
            menu()
        elif args.accion == "demo":
            demo(leer_numeros(args.valores) if args.valores else None)
        elif args.accion == "calidad":
            return 0 if calidad(esperar=False) else 1
        elif args.accion == "graficas":
            segundos = medir_y_graficar(aleatorio_con_semilla(2026), "aleatorio",
                                        "aleatoria", args.n_max)
            print(f"  ✔ Listo en {segundos:.0f} s → "
                  f"{CARPETA_GRAFICAS.relative_to(RAIZ)}")
            if not args.sin_ventana:
                visor.mostrar(CARPETA_GRAFICAS)
    except (KeyboardInterrupt, EOFError):
        print("\n  Programa cerrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
