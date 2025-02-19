from src.solvers.simplex import Simplex

class JuegoSumaCero:
    def __init__(self, matriz_pagos):
        self.matriz_pagos = matriz_pagos
        self.m = len(matriz_pagos)   # Número de estrategias del Jugador A
        self.n = len(matriz_pagos[0]) # Número de estrategias del Jugador B

    def resolver_jugador(self, jugador):
        if jugador == "A":
            # Definir la función objetivo: Max v
            c = [0] * self.m + [-1]

            # Construcción de restricciones P * x - v >= 0
            A = []
            for j in range(self.n):
                fila = [self.matriz_pagos[i][j] for i in range(self.m)] + [-1]
                A.append(fila)

            # Restricción de distribución de probabilidad: x1 + x2 + ... + xm = 1
            A.append([1] * self.m + [0])

            # Vector b
            b = [0] * self.n + [1]

            # Signos de restricciones
            signos = ['>='] * self.n + ['=']

        else:  # Jugador B
            # Definir la función objetivo: Min v (convertido en maximizador)
            c = [0] * self.n + [1]

            # Construcción de restricciones: P^T * y - v <= 0
            A = []
            for i in range(self.m):
                fila = [self.matriz_pagos[i][j] for j in range(self.n)] + [-1]
                A.append(fila)

            # Restricción de distribución de probabilidad: y1 + y2 + ... + yn = 1
            A.append([1] * self.n + [0])

            # Vector b
            b = [0] * self.m + [1]

            # Signos de restricciones
            signos = ['<='] * self.m + ['=']

        # Resolver con Simplex
        solver = Simplex(c, A, b, signos)
        solucion, valor, iterations = solver.resolver()

        # Extraer las estrategias
        estrategias = solucion[:-1]  # Excluir el valor del juego

        iterations = "Jugador " + jugador + "\n" + iterations
        return estrategias, valor, iterations

    def resolver(self):
        """
        Resuelve el juego para ambos jugadores utilizando Simplex.
        :return: Estrategias óptimas y valor del juego para ambos.
        """
        estrategias_a, valor_a, iterations_a = self.resolver_jugador("A")
        estrategias_b, valor_b, iterations_b = self.resolver_jugador("B")

        return {
            "Jugador_A": {"Estrategias": estrategias_a, "Valor_Juego": -valor_a, "Iterations": iterations_a},
            "Jugador_B": {"Estrategias": estrategias_b, "Valor_Juego": valor_b,  "Iterations": iterations_b},
        }

if __name__ == "__main__":
    # Definimos una matriz de pagos
    matriz_pagos = [
        [3, -2],
        [-1, 4]
    ]

    # Creamos el juego
    juego = JuegoSumaCero(matriz_pagos)

    # Resolvemos
    resultado = juego.resolver()

    # Mostramos los resultados
    print(resultado)
