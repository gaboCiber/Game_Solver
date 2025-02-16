import unittest
from src.juego_suma_cero import JuegoSumaCero

class TestJuegoSumaCero(unittest.TestCase):
    def test_juego_2x2(self):
        matriz_pagos = [
            [3, -2],
            [-1, 4]
        ]
        juego = JuegoSumaCero(matriz_pagos)
        resultados = juego.resolver()
        self.assertAlmostEqual(resultados["Jugador_A"]["Valor_Juego"], 1.4, places=1)
        self.assertAlmostEqual(resultados["Jugador_B"]["Valor_Juego"], 1.4, places=1)

if __name__ == "__main__":
    unittest.main()