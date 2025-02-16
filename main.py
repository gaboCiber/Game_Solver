from src.juego_suma_cero import JuegoSumaCero
from src.utils import cargar_matriz_desde_json, validar_matriz

def main():
    # Cargar matriz de pagos desde un archivo JSON
    matriz_pagos = cargar_matriz_desde_json("data/ejemplos.json")

    # Validar matriz
    if not validar_matriz(matriz_pagos):
        print("Error: La matriz de pagos no es válida.")
        return

    # Resolver el juego
    juego = JuegoSumaCero(matriz_pagos)
    resultados = juego.resolver()

    # Mostrar resultados
    print("Resultados para el Jugador A:", resultados["Jugador_A"])
    print("Resultados para el Jugador B:", resultados["Jugador_B"])

if __name__ == "__main__":
    main()