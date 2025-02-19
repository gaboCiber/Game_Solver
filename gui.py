import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QFileDialog, QWidget, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from src.juego_suma_cero import JuegoSumaCero
from src.utils import cargar_matriz_desde_json, validar_matriz

class JuegoSumaCeroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Juego de Suma Cero')
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        main_layout = QVBoxLayout()

        # Botón para cargar archivo JSON
        self.load_button = QPushButton('Cargar Matriz desde JSON', self)
        self.load_button.clicked.connect(self.cargar_matriz)
        main_layout.addWidget(self.load_button)

        # Área para mostrar la matriz de pagos
        self.matrix_table = QTableWidget(self)
        main_layout.addWidget(QLabel('Matriz de Pagos:'))
        main_layout.addWidget(self.matrix_table)

        # Botón para resolver el juego
        self.solve_button = QPushButton('Resolver Juego', self)
        self.solve_button.clicked.connect(self.resolver_juego)
        main_layout.addWidget(self.solve_button)

        # Área para mostrar los resultados
        self.results_display = QTextEdit(self)
        self.results_display.setReadOnly(True)
        main_layout.addWidget(QLabel('Resultados:'))
        main_layout.addWidget(self.results_display)

        # Botón para mostrar iteraciones
        self.iterations_button = QPushButton('Mostrar Iteraciones', self)
        self.iterations_button.clicked.connect(self.mostrar_iteraciones)
        main_layout.addWidget(self.iterations_button)

        # Crear pestañas para las iteraciones
        self.iterations_tabs = QTabWidget(self)
        self.iterations_tabs.setVisible(False)  # Ocultar inicialmente
        main_layout.addWidget(self.iterations_tabs)

        # Botón para limpiar resultados
        self.clear_button = QPushButton('Limpiar Resultados', self)
        self.clear_button.clicked.connect(self.limpiar_resultados)
        main_layout.addWidget(self.clear_button)

        # Botón para salir
        self.exit_button = QPushButton('Salir', self)
        self.exit_button.clicked.connect(self.close)
        main_layout.addWidget(self.exit_button)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Variables
        self.matriz_pagos = None
        self.resultados = None

    def cargar_matriz(self):
        # Abrir diálogo para seleccionar archivo JSON
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Cargar Matriz de Pagos", "", "JSON Files (*.json)", options=options)
        if file_name:
            self.matriz_pagos = cargar_matriz_desde_json(file_name)["matriz_pagos"]
            if validar_matriz(self.matriz_pagos):
                self.mostrar_matriz(self.matriz_pagos)
            else:
                QMessageBox.critical(self, "Error", "La matriz de pagos no es válida.")

    def mostrar_matriz(self, matrix):
        self.matrix_table.setRowCount(len(matrix))
        self.matrix_table.setColumnCount(len(matrix[0]) if len(matrix) > 0 else 0)

        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                self.matrix_table.setItem(i, j, QTableWidgetItem(str(value)))

    def resolver_juego(self):
        if self.matriz_pagos is None:
            QMessageBox.warning(self, "Advertencia", "No se ha cargado ninguna matriz de pagos.")
            return

        juego = JuegoSumaCero(self.matriz_pagos)
        self.resultados = juego.resolver()

        # Mostrar resultados
        resultados_text = f"Resultados para el Jugador A:\nEstrategias: {self.resultados['Jugador_A']['Estrategias']}\nValor del Juego: {self.resultados['Jugador_A']['Valor_Juego']}\n\n"
        resultados_text += f"Resultados para el Jugador B:\nEstrategias: {self.resultados['Jugador_B']['Estrategias']}\nValor del Juego: {self.resultados['Jugador_B']['Valor_Juego']}"
        self.results_display.setText(resultados_text)

        # Habilitar el botón de iteraciones
        self.iterations_button.setEnabled(True)

    def mostrar_iteraciones(self):
        if self.resultados is None:
            QMessageBox.warning(self, "Advertencia", "No hay iteraciones para mostrar.")
            return

        # Limpiar pestañas anteriores
        self.iterations_tabs.clear()

        # Crear pestañas para cada jugador
        tab_a = QTextEdit(self)
        tab_a.setPlainText(self.resultados['Jugador_A']['Iterations'])
        self.iterations_tabs.addTab(tab_a, "Jugador A")

        tab_b = QTextEdit(self)
        tab_b.setPlainText(self.resultados['Jugador_B']['Iterations'])
        self.iterations_tabs.addTab(tab_b, "Jugador B")

        # Mostrar las pestañas
        self.iterations_tabs.setVisible(True)

    def limpiar_resultados(self):
        self.results_display.clear()
        self.matrix_table.clear()
        self.matrix_table.setRowCount(0)
        self.matrix_table.setColumnCount(0)
        self.iterations_tabs.clear()
        self.iterations_tabs.setVisible(False)
        self.matriz_pagos = None
        self.resultados = None
        self.iterations_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JuegoSumaCeroApp()
    ex.show()
    sys.exit(app.exec_())