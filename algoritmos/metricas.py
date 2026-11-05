"""
metricas.py
===========

Contador de operaciones elementales que usan los tres algoritmos.

¿Por qué contar operaciones y no solo medir tiempo?
---------------------------------------------------
El tiempo en segundos depende del computador, del sistema operativo y hasta de
qué otros programas estén abiertos. En cambio, el NÚMERO DE COMPARACIONES que
hace un algoritmo depende solo de sus datos de entrada. Por eso es la medida
que mejor se compara con la función teórica f(n) de la notación Big O.

Se cuentan dos operaciones:

* ``comparaciones``: cada vez que el algoritmo compara dos elementos (a > b).
* ``movimientos``:   cada vez que un elemento se escribe en otra posición del
  arreglo (un desplazamiento o la mitad de un intercambio).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metricas:
    """Acumula las operaciones elementales de una ejecución.

    Attributes:
        comparaciones: número de comparaciones entre elementos.
        movimientos:   número de escrituras de elementos en el arreglo.
        pasadas:       número de pasadas (o de "gaps") que hizo el algoritmo.
    """

    comparaciones: int = 0
    movimientos: int = 0
    pasadas: int = 0

    def reiniciar(self) -> None:
        """Deja todos los contadores en cero para reutilizar el objeto."""
        self.comparaciones = 0
        self.movimientos = 0
        self.pasadas = 0

    def __str__(self) -> str:
        return (f"comparaciones={self.comparaciones:,}  "
                f"movimientos={self.movimientos:,}  pasadas={self.pasadas}")
