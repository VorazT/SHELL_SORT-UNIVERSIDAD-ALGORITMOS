# Pseudocódigo de los tres algoritmos

Convenciones: los arreglos empiezan en la posición 0, `n` es la cantidad de
elementos, `←` es asignación y `▷` marca un comentario.

---

## 1. Shell Sort (algoritmo propio) — gaps de Knuth

```text
SHELLSORT(A, n)
    h ← 1
    mientras h < n / 3 hacer              ▷ calcular el gap inicial: 1, 4, 13, 40...
        h ← 3·h + 1
    mientras h ≥ 1 hacer
        para i ← h hasta n - 1 hacer       ▷ Insertion Sort "con saltos" de tamaño h
            temp ← A[i]
            j ← i
            mientras j ≥ h y A[j - h] > temp hacer
                A[j] ← A[j - h]            ▷ el mayor se corre h posiciones
                j ← j - h
            A[j] ← temp
        h ← (h - 1) / 3                    ▷ siguiente gap, más pequeño
    retornar A
```

**Idea:** con gaps grandes los elementos viajan lejos en pocos pasos; cuando
`h = 1` el arreglo ya está casi ordenado y la última pasada (un Insertion Sort
normal) es muy rápida.

Código: [`algoritmos/shell_sort.py`](../algoritmos/shell_sort.py)

---

## 2. Insertion Sort

```text
INSERTIONSORT(A, n)
    para i ← 1 hasta n - 1 hacer
        temp ← A[i]                         ▷ la "carta" que se va a insertar
        j ← i
        mientras j > 0 y A[j - 1] > temp hacer
            A[j] ← A[j - 1]                 ▷ se corre UNA posición
            j ← j - 1
        A[j] ← temp
    retornar A
```

**Relación con Shell Sort:** es exactamente el bucle interno de Shell Sort con
`h = 1`.

Código: [`algoritmos/insertion_sort.py`](../algoritmos/insertion_sort.py)

---

## 3. Heap Sort

```text
HEAPSORT(A, n)
    para i ← piso(n / 2) - 1 bajando hasta 0 hacer    ▷ 1. construir el heap máximo
        HUNDIR(A, i, n)
    para fin ← n - 1 bajando hasta 1 hacer            ▷ 2. sacar el máximo n - 1 veces
        intercambiar A[0], A[fin]                     ▷ el mayor queda al final
        HUNDIR(A, 0, fin)                             ▷ reparar el heap
    retornar A

HUNDIR(A, i, tamaño)
    mientras 2·i + 1 < tamaño hacer
        hijo ← 2·i + 1                                ▷ hijo izquierdo
        si hijo + 1 < tamaño y A[hijo + 1] > A[hijo] entonces
            hijo ← hijo + 1                           ▷ se elige el hijo mayor
        si A[hijo] > A[i] entonces
            intercambiar A[i], A[hijo]
            i ← hijo
        si no
            terminar                                  ▷ ya cumple la regla del heap
```

**Idea:** el heap guarda el mayor en la raíz (posición 0). Se manda al final,
se repara el heap y se repite; el arreglo se llena de atrás hacia adelante.

Código: [`algoritmos/heap_sort.py`](../algoritmos/heap_sort.py)
