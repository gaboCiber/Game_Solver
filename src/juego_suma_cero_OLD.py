from pulp import LpProblem, LpVariable, lpSum, value, LpMaximize, LpMinimize, GLPK_CMD, COIN_CMD
import seaborn as sns
import matplotlib.pyplot as plt

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
            return GLPK_CMD(msg=False, options=["--" + algoritmo.replace("-", "")])
        elif algoritmo in ["primalsimplex", "dualsimplex", "barrier"]:
            return COIN_CMD(msg=False, options=[algoritmo])
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
    
    def resolver(self, algoritmo='primalsimplex'):
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
    
    def visualizar_matriz(self):
        """
        Muestra un heatmap de la matriz de pagos.
        """
        plt.figure(figsize=(8, 6))
        sns.heatmap(self.matriz_pagos, annot=True, cmap="YlGnBu", fmt=".2f",
                    xticklabels=[f"B{j+1}" for j in range(self.n)],
                    yticklabels=[f"A{i+1}" for i in range(self.m)])
        plt.title("Matriz de Pagos")
        plt.xlabel("Estrategias del Jugador B")
        plt.ylabel("Estrategias del Jugador A")
        plt.show()
        
    def visualizar_estrategias(self, estrategias_a, estrategias_b):
        """
        Muestra gráficos de barras para las estrategias óptimas de ambos jugadores.
        :param estrategias_a: Lista de probabilidades para el Jugador A.
        :param estrategias_b: Lista de probabilidades para el Jugador B.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Gráfico para el Jugador A
        ax1.bar([f"A{i+1}" for i in range(self.m)], estrategias_a, color="skyblue")
        ax1.set_title("Estrategias Óptimas del Jugador A")
        ax1.set_xlabel("Estrategias")
        ax1.set_ylabel("Probabilidad")

        # Gráfico para el Jugador B
        ax2.bar([f"B{j+1}" for j in range(self.n)], estrategias_b, color="lightgreen")
        ax2.set_title("Estrategias Óptimas del Jugador B")
        ax2.set_xlabel("Estrategias")
        ax2.set_ylabel("Probabilidad")

        plt.tight_layout()
        plt.show()