# Calidad de software — Shell Sort

**Resultado:** 16/16 verificaciones aprobadas en 0.13 s

Complejidad documentada: mejor Θ(n log n) · promedio ≈ O(n^1.25) · peor O(n^1.5) · no estable · in-place O(1)

| # | Verificación | Estado | Detalle |
|---|---|---|---|
| 1 | Arreglo vacío | ✅ | igual a sorted() (n=0) |
| 2 | Un solo elemento | ✅ | igual a sorted() (n=1) |
| 3 | Dos elementos desordenados | ✅ | igual a sorted() (n=2) |
| 4 | Ya ordenado (mejor caso) | ✅ | igual a sorted() (n=20) |
| 5 | Orden inverso | ✅ | igual a sorted() (n=20) |
| 6 | Con valores repetidos | ✅ | igual a sorted() (n=7) |
| 7 | Todos iguales | ✅ | igual a sorted() (n=15) |
| 8 | Negativos y decimales | ✅ | igual a sorted() (n=6) |
| 9 | Cadenas de texto | ✅ | igual a sorted() (n=5) |
| 10 | No modifica la entrada | ✅ | lista original intacta |
| 11 | Acepta cualquier secuencia (tupla) | ✅ | (9, 4, 7, 1) → [1, 4, 7, 9] |
| 12 | 1000 arreglos aleatorios quedan ordenados | ✅ | 0 fallos |
| 13 | Salida es permutación de la entrada | ✅ | 0 valores perdidos o inventados |
| 14 | Métricas no alteran el resultado | ✅ | mismo resultado con contador |
| 15 | Mejor caso: comparaciones = fórmula | ✅ | exacto en n = 1 … 1000 |
| 16 | Estabilidad coincide con la documentación | ✅ | observado = documentado (no estable) |
