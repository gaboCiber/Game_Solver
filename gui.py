import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QWidget
from PyQt5.QtCore import Qt
from src.juego_suma_cero import JuegoSumaCero
from src.utils import cargar_matriz_desde_json, validar_matriz

class JuegoSumaCeroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Juego de Suma Cero')
        self.setGeometry(100, 100, 600, 400)

        # Layout principal
        main_layout = QVBoxLayout()

        # Botón para cargar archivo JSON
        self.load_button = QPushButton('Cargar Matriz desde JSON', self)
        self.load_button.clicked.connect(self.cargar_matriz)
        main_layout.addWidget(self.load_button)

        # Área para mostrar la matriz de pagos
        self.matrix_display = QTextEdit(self)
        self.matrix_display.setReadOnly(True)
        main_layout.addWidget(QLabel('Matriz de Pagos:'))
        main_layout.addWidget(self.matrix_display)

        # Botón para resolver el juego
        self.solve_button = QPushButton('Resolver Juego', self)
        self.solve_button.clicked.connect(self.resolver_juego)
        main_layout.addWidget(self.solve_button)

        # Área para mostrar los resultados
        self.results_display = QTextEdit(self)
        self.results_display.setReadOnly(True)
        main_layout.addWidget(QLabel('Resultados:'))
        main_layout.addWidget(self.results_display)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Variables
        self.matriz_pagos = None

    def cargar_matriz(self):
        # Abrir diálogo para seleccionar archivo JSON
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Cargar Matriz de Pagos", "", "JSON Files (*.json)", options=options)
        if file_name:
            self.matriz_pagos = cargar_matriz_desde_json(file_name)
            if validar_matriz(self.matriz_pagos):
                self.matrix_display.setText(self.format_matrix(self.matriz_pagos))
            else:
                self.matrix_display.setText("Error: La matriz de pagos no es válida.")

    def resolver_juego(self):
        if self.matriz_pagos is None:
            self.results_display.setText("Error: No se ha cargado ninguna matriz de pagos.")
            return

        juego = JuegoSumaCero(self.matriz_pagos)
        resultados = juego.resolver()

        # Mostrar resultados
        resultados_text = f"Resultados para el Jugador A:\nEstrategias: {resultados['Jugador_A']['Estrategias']}\nValor del Juego: {resultados['Jugador_A']['Valor_Juego']}\n\n"
        resultados_text += f"Resultados para el Jugador B:\nEstrategias: {resultados['Jugador_B']['Estrategias']}\nValor del Juego: {resultados['Jugador_B']['Valor_Juego']}"
        self.results_display.setText(resultados_text)

    def format_matrix(self, matrix):
        return "\n".join(["\t".join(map(str, row)) for row in matrix])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JuegoSumaCeroApp()
    ex.show()
    sys.exit(app.exec_())