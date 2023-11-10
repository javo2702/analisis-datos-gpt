import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog, \
    QTableWidgetItem, QTableWidget, QHBoxLayout, QInputDialog, QLabel, QComboBox, QDialog
import pandas as pd
from matplotlib.backends.backend_template import FigureCanvas
import pyqtgraph as pg
from excel.excel import clean_data
from gpt.functions import ask_gpt
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ExcelReaderApp(QMainWindow):
    df_cleaned = None
    user_request = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visor de Excel")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table_label = QLabel("Datos a Analizar")
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_label)
        self.layout.addWidget(self.table_widget)

        self.text_label = QLabel("Prompt para GPT")
        self.text_edit = QTextEdit()
        self.text_edit.setFixedHeight(100)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.text_edit)

        self.text_label_response = QLabel("Respuesta de GPT")
        self.text_response = QTextEdit()
        self.text_response.setFixedHeight(100)
        self.layout.addWidget(self.text_label_response)
        self.layout.addWidget(self.text_response)

        self.load_button = QPushButton("Cargar Archivo Excel")
        self.load_button.setFixedHeight(40)
        self.analyze_button = QPushButton("Analizar datos")
        self.analyze_button.setFixedHeight(40)
        self.prompt_button = QPushButton("Ingresar consulta")
        self.prompt_button.setFixedHeight(40)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.load_button)
        self.buttons_layout.addWidget(self.prompt_button)
        self.buttons_layout.addWidget(self.analyze_button)

        self.layout.addLayout(self.buttons_layout)

        self.column_x_label = QLabel("Seleccionar Columna X:")
        self.combo_x = QComboBox()
        self.layout.addWidget(self.column_x_label)
        self.layout.addWidget(self.combo_x)

        self.column_y_label = QLabel("Seleccionar Columna Y:")
        self.combo_y = QComboBox()
        self.layout.addWidget(self.column_y_label)
        self.layout.addWidget(self.combo_y)

        self.chart_type_label = QLabel("Tipo de Gráfico:")
        self.combo_chart_type = QComboBox()
        self.combo_chart_type.addItems(["Scatter", "Bar"])
        self.layout.addWidget(self.chart_type_label)
        self.layout.addWidget(self.combo_chart_type)

        self.generate_chart_button = QPushButton("Generar Gráfico")
        self.generate_chart_button.setFixedHeight(40)
        self.layout.addWidget(self.generate_chart_button)
        self.generate_chart_button.clicked.connect(self.generate_chart)

        self.load_button.clicked.connect(self.load_excel)
        self.prompt_button.clicked.connect(self.get_text_from_user)
        self.analyze_button.clicked.connect(self.analyze_data_gpt)

    def load_excel(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "",
                                                   "Archivos de Excel (*.xlsx);;Todos los archivos (*)",
                                                   options=options)

        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.df_cleaned = df.dropna()  # Eliminar filas vacías
                text_data = self.df_cleaned.to_string(index=False)
                request = "¿Puedes proporcionar un analisis de los siguientes datos?" + "\n" + text_data
                print(f"${request}")
                self.display_excel_data(self.df_cleaned)
                self.update_combo_boxes()
                self.text_edit.setPlainText(request)
                self.combo_chart_type.setCurrentIndex(0)
            except Exception as e:
                print(f"Error al cargar el archivo: {str(e)}")

    def get_text_from_user(self):
        text, ok_pressed = QInputDialog.getText(self, "Ingresar Pregunta",
                                                "Por favor, ingresa una pregunta para hacerle a GPT sobre los datos cargados:")

        if ok_pressed:
            self.user_request = text
            text_data = self.df_cleaned.to_string(index=False)
            request = self.user_request + "\n" + text_data
            self.text_edit.setPlainText(request)

    def analyze_data_gpt(self):
        try:
            response = ask_gpt("What's your analysis about those data?", self.df_cleaned)
            self.text_response.setPlainText(response["choices"])
        except Exception as e:
            print(f"Error al cargar el archivo: {str(e)}")

    def display_excel_data(self, data):
        self.table_widget.clear()
        self.table_widget.setRowCount(len(data.index))
        self.table_widget.setColumnCount(len(data.columns))
        self.table_widget.setHorizontalHeaderLabels(data.columns)

        for row_index, row in data.iterrows():
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row_index, col_index, item)

    def generate_chart(self):
        selected_column_x = self.combo_x.currentText()
        selected_column_y = self.combo_y.currentText()
        chart_type = self.combo_chart_type.currentText()

        if not selected_column_x or not selected_column_y:
            return  # Evita errores si no se seleccionaron columnas

        try:
            win = pg.plot()
            if chart_type == "Scatter":
                win.plot(self.df_cleaned[selected_column_x], self.df_cleaned[selected_column_y], pen=None, symbol='o')
            elif chart_type == "Bar":
                x_data = [0] + list(self.df_cleaned[selected_column_x])
                y_data = [0] + list(self.df_cleaned[selected_column_y])
                win.plot(x_data, y_data, stepMode=True, fillLevel=0)
        except Exception as e:
                print(f"Error al generar el chart: {str(e)}")

    def update_combo_boxes(self):
        if self.df_cleaned is not None:
            column_names = self.df_cleaned.columns.tolist()
            self.combo_x.clear()
            self.combo_y.clear()
            self.combo_x.addItems(column_names)
            self.combo_y.addItems(column_names)


def paint_ui():
    app = QApplication(sys.argv)
    window = ExcelReaderApp()
    window.show()
    sys.exit(app.exec_())
