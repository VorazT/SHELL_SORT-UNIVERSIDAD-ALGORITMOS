# Análisis de algoritmos: Shell Sort vs Insertion Sort vs Heap Sort

Producto didáctico y comparativo de ordenamiento en **Python**.
Algoritmo propio: **Shell Sort**. Se compara con dos métodos de la lista del curso:

| Algoritmo | Papel en el trabajo | Por qué se eligió |
|---|---|---|
| **Shell Sort** | Algoritmo propio | — |
| **Insertion Sort** | Su "papá" | Shell Sort es un Insertion Sort con saltos: cuando el gap llega a 1, hace exactamente un Insertion Sort. |
| **Heap Sort** | Su "rival" | Mismo perfil que Shell Sort (in-place, memoria O(1), no estable, mucho mejor que O(n²)), pero con Θ(n log n) **garantizado**. |

---

## ✅ Cumplimiento de los requerimientos

| Requerimiento | Dónde está |
|---|---|
| 1. Tres métodos (propio + dos) | `algoritmos/shell_sort.py`, `insertion_sort.py`, `heap_sort.py` |
| 2. Historia, características y Big O de cada uno | Docstring de cada archivo de `algoritmos/` y la tabla de abajo |
| 3. Calidad de software de cada algoritmo por separado | `calidad/verificador.py` (16 verificaciones por algoritmo) y `tests/test_<algoritmo>.py` (pytest) |
| 3.1 Gráficas generadas por el programa, rango de arreglos aumentado | `analisis/graficas.py` → `resultados/graficas/` (n de 500 a 5.000 y rango ampliado hasta 50.000) |
| 4. Pseudocódigo | `docs/pseudocodigo.md` y el docstring de cada algoritmo |

---

## 🚀 Cómo ejecutarlo (VS Code)

```bash
# 1. Instalar dependencias (una sola vez)
python -m pip install -r requirements.txt

# 2. Menú interactivo
python main.py

# o directamente:
python main.py demo                  # Shell Sort paso a paso con tus números
python main.py demo --valores "35 33 42 10 14 19 27 44"
python main.py calidad               # verificación de calidad de los 3
python main.py graficas              # mediciones + gráficas (≈ 30 s)
python main.py graficas --rapido     # versión corta para probar
python main.py graficas --n-max 10000 --n-ampliado 100000   # rango más grande
python main.py todo                  # calidad + gráficas

# 3. Pruebas unitarias
python -m pytest -v
```

En VS Code también están listas las configuraciones de ejecución (`.vscode/launch.json`)
y la pestaña **Testing** detecta las pruebas automáticamente.

---

## 📁 Estructura

```text
analisis-shell-sort/
├── main.py                    # programa principal (menú y comandos)
├── algoritmos/
│   ├── shell_sort.py          # ★ algoritmo propio + secuencias de gaps
│   ├── insertion_sort.py
│   ├── heap_sort.py
│   └── metricas.py            # contador de comparaciones y movimientos
├── analisis/
│   ├── generadores.py         # arreglos aleatorio / ordenado / inverso
│   ├── benchmark.py           # cuenta operaciones y mide tiempo
│   ├── complejidad.py         # funciones f(n) y ajuste c·f(n) con R²
│   └── graficas.py            # todas las gráficas (matplotlib)
├── calidad/
│   └── verificador.py         # 16 verificaciones de calidad por algoritmo
├── tests/                     # pytest: un archivo por algoritmo
├── docs/pseudocodigo.md
└── resultados/
    ├── graficas/              # PNG generados por el programa
    ├── datos/                 # CSV con las mediciones (abren en Excel)
    └── calidad/               # informe de calidad de cada algoritmo
```

---

## 📊 Resumen de complejidad

| | Shell Sort (Knuth) | Insertion Sort | Heap Sort |
|---|---|---|---|
| **Mejor caso** | Θ(n log n) | Θ(n) | Θ(n log n) |
| **Caso promedio** | ≈ O(n^1.25) (empírico) | Θ(n²) | Θ(n log n) |
| **Peor caso** | O(n^1.5) | Θ(n²) | Θ(n log n) |
| **Memoria extra** | O(1) | O(1) | O(1) |
| **Estable** | No | Sí | No |
| **Adaptativo** | Sí | Sí | No |

### ¿Cómo se comprueba Big O con las gráficas?

El programa **cuenta las comparaciones** (no dependen del computador) y **mide el tiempo**
para tamaños crecientes de arreglo. Luego busca la constante `c` que mejor acerca
`c·f(n)` a lo medido (mínimos cuadrados) y reporta **R²**: si R² ≈ 1, la función f(n)
de Big O describe el crecimiento real. Ejemplo de una ejecución:

| Algoritmo | Caso | Ajuste obtenido | R² |
|---|---|---|---|
| Insertion | inverso | 0.4999·n² (teoría: n(n−1)/2) | 1.0000 |
| Insertion | aleatorio | 0.25·n² (teoría: n²/4) | 0.9996 |
| Shell | aleatorio | 2.39·n^1.25 | 0.999 |
| Heap | aleatorio | 1.74·n·log₂n | 0.9998 |

---

## 📜 Historia breve

- **Shell Sort (1959)** — Donald L. Shell, *"A High-Speed Sorting Procedure"*,
  Communications of the ACM. Uno de los primeros en romper la barrera O(n²).
  Mejores secuencias de gaps: Hibbard (1963), Knuth (1973), Sedgewick (1986), Ciura (2001).
- **Insertion Sort** — método antiguo (así se ordenan las cartas). Knuth registra que
  John Mauchly ya trató la inserción en 1946, en las conferencias de la Moore School.
- **Heap Sort (1964)** — J. W. J. Williams (*Algorithm 232*, CACM), quien también creó el
  heap binario. R. W. Floyd lo mejoró ese mismo año (construcción del heap en O(n)).

## 📚 Referencias

- Shell, D. L. (1959). A high-speed sorting procedure. *Communications of the ACM, 2*(7), 30–32.
- Williams, J. W. J. (1964). Algorithm 232: Heapsort. *Communications of the ACM, 7*(6), 347–348.
- Floyd, R. W. (1964). Algorithm 245: Treesort 3. *Communications of the ACM, 7*(12), 701.
- Knuth, D. E. (1998). *The Art of Computer Programming, Vol. 3: Sorting and Searching* (2.ª ed.). Addison-Wesley.
- Ciura, M. (2001). Best increments for the average case of Shellsort. *FCT 2001*, LNCS 2138, 106–117.
- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4.ª ed.). MIT Press.
- Sedgewick, R., & Wayne, K. (2011). *Algorithms* (4.ª ed.). Addison-Wesley.
