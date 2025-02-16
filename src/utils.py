import json

def cargar_matriz_desde_json(ruta_archivo):
    """
    Carga una matriz de pagos desde un archivo JSON.
    :param ruta_archivo: Ruta al archivo JSON.
    :return: Matriz de pagos (lista de listas).
    """
    with open(ruta_archivo, "r") as f:
        datos = json.load(f)
    return datos["matriz_pagos"]

def validar_matriz(matriz):
    """
    Valida que la matriz de pagos sea válida (m x n, con valores numéricos).
    :param matriz: Matriz de pagos.
    :return: True si es válida, False en caso contrario.
    """
    if not isinstance(matriz, list) or not all(isinstance(fila, list) for fila in matriz):
        return False
    m = len(matriz)
    n = len(matriz[0]) if m > 0 else 0
    return all(len(fila) == n for fila in matriz) and all(
        isinstance(valor, (int, float)) for fila in matriz for valor in fila
    )