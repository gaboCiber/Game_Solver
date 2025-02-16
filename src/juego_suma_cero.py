from pulp import LpMaximize,LpMinimize, LpProblem, LpVariable, lpSum, value

class JuegoSumaCero:
    def __init__(self, matriz_pagos):
        """
        Inicializa el juego con una matriz de pagos.
        :param matriz_pagos: Lista de listas (matriz m x n) que representa los pagos.
        """
        self.matriz_pagos = matriz_pagos
        self.m = len(matriz_pagos)  # Número de estrategias del Jugador A
        self.n = len(matriz_pagos[0])  # Número de estrategias del Jugador B

    def resolver_jugador_a(self):
        """
        Resuelve el problema para el Jugador A (maximizador).
        :return: Estrategias óptimas y valor del juego.
        """
        prob = LpProblem("Jugador_A", LpMaximize)
        x = [LpVariable(f"x{i}", 0, 1) for i in range(self.m)]  # Variables de decisión
        v = LpVariable("v")  # Valor del juego

        # Función objetivo
        prob += v

        # Restricciones
        for j in range(self.n):
            prob += lpSum([self.matriz_pagos[i][j] * x[i] for i in range(self.m)]) >= v
        prob += lpSum(x) == 1  # Las probabilidades deben sumar 1

        # Resolver
        prob.solve()

        # Extraer resultados
        estrategias = [value(x[i]) for i in range(self.m)]
        valor_juego = value(v)
        return estrategias, valor_juego
    
    def resolver_jugador_b(self):
        """
        Resuelve el problema para el Jugador B (minimizador).
        :return: Estrategias óptimas y valor del juego.
        """
        prob = LpProblem("Jugador_B", LpMinimize)  # Usar LpMinimize directamente
        y = [LpVariable(f"y{j}", 0, 1) for j in range(self.n)]  # Variables de decisión
        v = LpVariable("v")  # Valor del juego

        # Función objetivo
        prob += v  # Minimizar v

        # Restricciones
        for i in range(self.m):
            prob += lpSum([self.matriz_pagos[i][j] * y[j] for j in range(self.n)]) <= v
        prob += lpSum(y) == 1  # Las probabilidades deben sumar 1

        # Resolver
        prob.solve()

        # Extraer resultados
        estrategias = [value(y[j]) for j in range(self.n)]
        valor_juego = value(v)
        return estrategias, valor_juego

    def resolver(self):
        """
        Resuelve el juego para ambos jugadores.
        :return: Estrategias óptimas y valor del juego para ambos.
        """
        estrategias_a, valor_a = self.resolver_jugador_a()
        estrategias_b, valor_b = self.resolver_jugador_b()
        return {
            "Jugador_A": {"Estrategias": estrategias_a, "Valor_Juego": valor_a},
            "Jugador_B": {"Estrategias": estrategias_b, "Valor_Juego": valor_b},
        }