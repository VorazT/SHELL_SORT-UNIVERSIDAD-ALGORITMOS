"""
Casos de prueba compartidos por los tres archivos de pruebas.

Cada archivo ``test_<algoritmo>.py`` usa estos casos con SU algoritmo, así cada
algoritmo se verifica por separado, y además agrega pruebas propias.
"""

import random

#: (descripción, entrada) — casos borde que todo ordenamiento debe resolver.
CASOS_BORDE = [
    ("vacio", []),
    ("un_elemento", [1]),
    ("dos_desordenados", [2, 1]),
    ("ordenado", list(range(50))),
    ("inverso", list(range(50, 0, -1))),
    ("repetidos", [4, 1, 4, 2, 1, 4, 3, 2]),
    ("todos_iguales", [9] * 30),
    ("negativos", [-3, 10, -50, 0, 7, -1]),
    ("decimales", [0.5, -1.25, 3.75, 0.0, 2.5]),
    ("texto", ["mango", "lulo", "guayaba", "feijoa", "banano"]),
    ("tamano_primo", random.Random(1).sample(range(1000), 97)),
]


def arreglos_aleatorios(cantidad=300, semilla=11):
    """Genera arreglos aleatorios de tamaños entre 0 y 300."""
    rng = random.Random(semilla)
    for _ in range(cantidad):
        n = rng.randint(0, 300)
        yield [rng.randint(-500, 500) for _ in range(n)]


class Clave:
    """Valor comparado solo por ``clave``; ``origen`` marca su posición inicial."""

    def __init__(self, clave, origen):
        self.clave, self.origen = clave, origen

    def __gt__(self, otro):
        return self.clave > otro.clave

    def __lt__(self, otro):
        return self.clave < otro.clave
