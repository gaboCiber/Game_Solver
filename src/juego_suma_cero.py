from pulp import LpProblem, LpVariable, lpSum, value, LpMaximize, LpMinimize, GLPK_CMD, COIN_CMD

class JuegoSumaCero:
    def __init__(self, matriz_pagos, algoritmo="dual"):
        self.matriz_pagos = matriz_pagos
        self.m = len(matriz_pagos)
        self.n = len(matriz_pagos[0])

    def _mapear_algoritmo_a_solver(self, algoritmo='dual'):
        """
        Define qué solver y opciones usar según el algoritmo elegido.
        """
        if algoritmo in ["primal", "dual"]:
            return GLPK_CMD(options=["--" + algoritmo.replace("-", "")])
        elif algoritmo in ["primalsimplex", "dualsimplex", "barrier"]:
            return COIN_CMD(options=[algoritmo])
        else:
            raise ValueError(f"Algoritmo no soportado: {self.algoritmo}")

    def resolver_jugador(self, jugador, algoritmo='dual'):
        if jugador == "A":
            prob = LpProblem("Jugador_A", LpMaximize)
            variables = [LpVariable(f"x{i}", 0, 1) for i in range(self.m)]
        else:
            prob = LpProblem("Jugador_B", LpMinimize)
            variables = [LpVariable(f"y{j}", 0, 1) for j in range(self.n)]

        v = LpVariable("v")
        prob += v

        if jugador == "A":
            for j in range(self.n):
                prob += lpSum([self.matriz_pagos[i][j] * variables[i] for i in range(self.m)]) >= v
            prob += lpSum(variables) == 1
        else:
            for i in range(self.m):
                prob += lpSum([self.matriz_pagos[i][j] * variables[j] for j in range(self.n)]) <= v
            prob += lpSum(variables) == 1

        # Resolver con el solver y opciones configuradas
        prob.solve(solver=self._mapear_algoritmo_a_solver(algoritmo))
        
        return [value(var) for var in variables], value(v)
    
    def resolver(self, algoritmo='primal'):
        """
        Resuelve el juego para ambos jugadores.
        :return: Estrategias óptimas y valor del juego para ambos.
        """
        estrategias_a, valor_a = self.resolver_jugador('A', algoritmo)
        estrategias_b, valor_b = self.resolver_jugador('B', algoritmo)
        return {
            "Jugador_A": {"Estrategias": estrategias_a, "Valor_Juego": valor_a},
            "Jugador_B": {"Estrategias": estrategias_b, "Valor_Juego": valor_b},
        }
        