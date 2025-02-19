from src.juego_suma_cero import JuegoSumaCero as mine
from src.juego_suma_cero_OLD import JuegoSumaCero as other
from src.utils import cargar_matriz_desde_json, validar_matriz

def main():
    # Cargar matriz de pagos desde un archivo JSON
    ejemplos = cargar_matriz_desde_json("data/ejemplos.json")

    for number in ejemplos:
        matriz_pagos = ejemplos[number]
        # Validar matriz
        if not validar_matriz(matriz_pagos):
            print("Error: La matriz de pagos no es válida.")
            return

        # Resolver el juego
        juego = mine(matriz_pagos)
        resultados = juego.resolver()

        # Mostrar resultados
        print("Resultados para el Jugador A:", "Estrategias: ", resultados["Jugador_A"]['Estrategias'], ", Valor_Juego: ", resultados["Jugador_A"]['Valor_Juego'])
        print("Resultados para el Jugador B:", "Estrategias: ", resultados["Jugador_B"]['Estrategias'], ", Valor_Juego: ", resultados["Jugador_B"]['Valor_Juego'])

if __name__ == "__main__":
    main()