import sys
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, \
    QFileDialog, QTextBrowser, QHBoxLayout, QTableWidget, QTableWidgetItem, QProgressDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from gpt.functions import analyse_gpt


# Create a custom thread for the GPT analysis
class GPTAnalysisThread(QThread):
    analysis_completed = pyqtSignal(str)

    def __init__(self, final_promt):
        super().__init__()
        self.final_promt = final_promt

    def run(self):
        try:
            response = analyse_gpt(self.final_promt)
            self.analysis_completed.emit(response["choices"][0]['message']['content'])
        except Exception as e:
            self.analysis_completed.emit("Error al analizar los datos: " + str(e))


class ChartApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.df_cleaned = None
        self.data = None
        self.analysis_thread = None
        self.setWindowTitle("Analisis de Datos con GPT")
        self.setGeometry(100, 100, 1500, 800)

        # Layout principal de dos columnas
        self.main_layout = QHBoxLayout()
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()
        self.end_column = QVBoxLayout()

        self.filter_row = QHBoxLayout()
        self.data_group_row = QHBoxLayout()

        # Primera fila de la primera columna (combos para años y meses)
        self.year_combo1 = QComboBox()
        self.year_combo1.setFixedHeight(30)
        self.year_combo2 = QComboBox()
        self.year_combo2.setFixedHeight(30)
        self.month_combo1 = QComboBox()
        self.month_combo1.setFixedHeight(30)
        self.month_combo2 = QComboBox()
        self.month_combo2.setFixedHeight(30)
        self.filter_button = QPushButton("Filtrar")
        self.filter_button.setFixedHeight(30)

        self.filter_row.addWidget(self.year_combo1)
        self.filter_row.addWidget(self.month_combo1)
        self.filter_row.addWidget(self.year_combo2)
        self.filter_row.addWidget(self.month_combo2)
        self.filter_row.addWidget(self.filter_button)

        self.filter_label = QLabel("Filtro por fecha")
        self.left_column.addWidget(self.filter_label)
        self.left_column.addLayout(self.filter_row)

        # Segunda fila de la primera columna (visualización de datos del Excel)
        self.upload_button = QPushButton("Subir Data")
        self.upload_button.setFixedHeight(40)

        self.data_display = QTableWidget()
        self.left_column.addWidget(self.upload_button)
        self.data_label = QLabel("Datos cargados")
        self.left_column.addWidget(self.data_label)
        self.left_column.addWidget(self.data_display)

        # Tercera fila de la primera columna (combos para ejes X e Y)
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.setFixedHeight(40)
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.setFixedHeight(40)

        self.data_group_row.addWidget(self.x_axis_combo)
        self.data_group_row.addWidget(self.y_axis_combo)

        self.chart_column_label = QLabel("Columnas X, Y para chart")
        self.left_column.addWidget(self.chart_column_label)
        self.left_column.addLayout(self.data_group_row)

        # Cuarta fila de la primera columna (combo para elegir el tipo de gráfico)
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Scatter", "Bar", "Pie", "Line", "Histogram"])
        self.chart_type_combo.setFixedHeight(40)
        self.chart_type_label = QLabel("Gráfico")
        self.left_column.addWidget(self.chart_type_label)
        self.left_column.addWidget(self.chart_type_combo)

        # Quinta fila de la primera columna (botón para generar el gráfico)
        self.generate_button = QPushButton("Generar Gráfico")
        self.generate_button.setFixedHeight(40)
        self.left_column.addWidget(self.generate_button)

        # Segunda columna (visualización del gráfico, botón y área de texto)
        self.chart_canvas = FigureCanvas(plt.figure())
        self.chart_result_label = QLabel("Gráfico generado")
        self.right_column.addWidget(self.chart_result_label)
        self.right_column.addWidget(self.chart_canvas)
        self.analyze_button = QPushButton("Analizar Datos")
        self.analyze_button.setFixedHeight(40)
        self.right_column.addWidget(self.analyze_button)
        self.text_area = QTextBrowser()
        self.text_area.setReadOnly(True)
        self.response_gpt = QLabel("Análisis:")
        self.right_column.addWidget(self.response_gpt)
        self.right_column.addWidget(self.text_area)

        # Tercera columna (Visualización de la data en texto para GPT y logcat)
        self.data_gpt_text = QTextBrowser()
        self.data_gpt_text.setReadOnly(True)
        self.logcat = QTextBrowser()
        self.logcat.setFixedHeight(290)
        self.logcat.setReadOnly(True)

        self.gpt_text_label = QLabel("Datos del gráfico")
        self.end_column.addWidget(self.gpt_text_label)
        self.end_column.addWidget(self.data_gpt_text)
        self.logcat_label = QLabel("Logcat")
        self.end_column.addWidget(self.logcat_label)
        self.end_column.addWidget(self.logcat)

        # Agregar las dos columnas al layout principal
        self.main_layout.addLayout(self.left_column)
        self.main_layout.addLayout(self.right_column)
        self.main_layout.addLayout(self.end_column)

        # Crear un widget principal y establecer el layout principal
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        # Evento de carga de datos desde un archivo Excel
        self.generate_button.clicked.connect(self.generate_chart)
        self.upload_button.clicked.connect(self.upload_data)
        self.analyze_button.clicked.connect(self.analyze_data_gpt)

    def save_chart_data(self, chart_data):
        try:
            # Obtiene la ruta del directorio actual del script
            current_directory = os.path.dirname(os.path.abspath(__file__))
            # Define el nombre del archivo que deseas guardar
            file_name = "chart_data.txt"
            # Crea la ruta completa al archivo
            file_path = os.path.join(current_directory, file_name)
            if os.path.exists(file_path):
                # Si existe un archivo anterior, eliminarlo
                os.remove(file_path)
            # Guardar los datos del gráfico en un archivo de texto
            with open(file_path, "w") as file:
                for data_point in chart_data:
                    if isinstance(data_point, (list, tuple)) and len(data_point) >= 2:
                        file.write(f"{data_point[0]}, {data_point[1]}\n")
                    else:
                        file.write(f"{data_point}\n")
            self.upload_logcat("Archivo guardado correctamente")
            self.load_chart_data()
        except Exception as e:
            self.upload_logcat("Error al guardar el archivo: " + {str(e)})

    def load_chart_data(self):
        try:
            # Obtiene la ruta del directorio actual del script
            current_directory = os.path.dirname(os.path.abspath(__file__))
            # Define el nombre del archivo que deseas cargar
            file_name = "chart_data.txt"
            # Crea la ruta completa al archivo
            file_path = os.path.join(current_directory, file_name)

            if os.path.exists(file_path):
                # Cargar el contenido del archivo
                with open(file_path, "r") as file:
                    chart_data = file.read()
                    self.data = chart_data
                # Establecer el contenido en el QTextBrowser
                self.data_gpt_text.setPlainText(chart_data)
                self.upload_logcat("Datos cargados correctamente desde el archivo")
            else:
                self.upload_logcat("El archivo no existe.")
        except Exception as e:
            self.upload_logcat("Error al cargar el archivo: " + str(e))

    def generate_chart(self):
        selected_column_x = self.x_axis_combo.currentText()
        selected_column_y = self.y_axis_combo.currentText()
        chart_type = self.chart_type_combo.currentText()

        if not selected_column_x or not selected_column_y:
            return  # Evita errores si no se seleccionaron columnas

        try:
            plt.close()
            # Limpia el contenido anterior del canvas
            self.chart_canvas.figure.clf()
            chart_data = None
            plt.figure()
            plt.xlabel(selected_column_x)
            plt.ylabel(selected_column_y)
            if chart_type == "Scatter":
                chart_data = self.df_cleaned[[selected_column_x, selected_column_y]].values
                self.df_cleaned.plot(kind='scatter', x=selected_column_x, y=selected_column_y)
                plt.title('Gráfico de Dispersión')
            elif chart_type == "Bar":
                chart_data = self.df_cleaned[[selected_column_x, selected_column_y]].values
                self.df_cleaned.plot(kind='bar', x=selected_column_x, y=selected_column_y)
                plt.title('Gráfico de Barras')
            elif chart_type == "Pie":
                chart_data = self.df_cleaned[selected_column_y].values
                self.df_cleaned.plot(kind='pie', y=selected_column_y)
                plt.title('Gráfico circular')
            elif chart_type == "Line":
                chart_data = self.df_cleaned[[selected_column_x, selected_column_y]].values
                self.df_cleaned.plot(kind='line', x=selected_column_x, y=selected_column_y)
                plt.title('Gráfico de lineas')
            elif chart_type == "Histogram":
                chart_data = self.df_cleaned[selected_column_x].values
                self.df_cleaned[selected_column_x].plot(kind='hist')
                plt.title('Histograma')

            if chart_data is not None:
                # Mostrar el gráfico en chart_canvas
                self.chart_canvas.figure = plt.gcf()
                self.chart_canvas.draw()
                # Guardar los datos del gráfico en un archivo de texto
                self.save_chart_data(chart_data)
                self.upload_logcat("Gráfico generado correctamente")

        except Exception as e:
            self.upload_logcat("Error al generar el gráfico: " + {str(e)})

    def upload_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "",
                                                   "Archivos de Excel (*.xlsx);;Todos los archivos (*)",
                                                   options=options)

        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.df_cleaned = df.dropna()  # Eliminar filas vacías
                self.display_excel_data(self.df_cleaned)
                self.update_combo_boxes()
                self.chart_type_combo.setCurrentIndex(0)
            except Exception as e:
                print(f"Error al cargar el archivo: {str(e)}")

    def display_excel_data(self, data):
        self.data_display.clear()
        self.data_display.setRowCount(len(data.index))
        self.data_display.setColumnCount(len(data.columns))
        self.data_display.setHorizontalHeaderLabels(data.columns)

        for row_index, row in data.iterrows():
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_display.setItem(row_index, col_index, item)

        self.upload_logcat("Datos cargados correctamente")

    def upload_logcat(self, text):
        current_text = self.logcat.toPlainText()
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_text = text
        concatenated_text = current_text + "\n" + current_datetime + ": " + new_text

        self.logcat.setPlainText(concatenated_text)

    def update_combo_boxes(self):
        if self.df_cleaned is not None:
            column_names = self.df_cleaned.columns.tolist()
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            self.x_axis_combo.addItems(column_names)
            self.y_axis_combo.addItems(column_names)
            self.check_and_fill_date_comboboxes()

    def check_and_fill_date_comboboxes(self):
        date_column_name = "fecha"  # Reemplaza con el nombre de la columna de fecha real

        if date_column_name in self.df_cleaned.columns:
            date_data = self.df_cleaned[date_column_name]
            min_date = date_data.min()
            max_date = date_data.max()

            years = list(range(min_date.year, max_date.year + 1))
            months = list(range(1, 13))  # 1 a 12

            # Llena los ComboBox de años y meses con los valores calculados
            self.year_combo1.clear()
            self.year_combo1.addItems([str(year) for year in years])

            self.year_combo2.clear()
            self.year_combo2.addItems([str(year) for year in years])

            self.month_combo1.clear()
            self.month_combo1.addItems([str(month) for month in months])

            self.month_combo2.clear()
            self.month_combo2.addItems([str(month) for month in months])
        else:
            # No se encontró una columna de fecha
            print("La columna de fecha no se encontró en los datos.")

            self.upload_logcat("La columna de fecha no se encontró en los datos")

    def analyze_data_gpt(self):
        try:
            first_line_promt = "Según un gráfico del tipo " + self.chart_type_combo.currentText() + " con los siguientes datos: "
            datos = self.data
            selected_column_x = self.x_axis_combo.currentText()
            selected_column_y = self.y_axis_combo.currentText()
            columnas = "Cuyas columnas son " + selected_column_x + " y " + selected_column_y
            question = "¿cúal es tu análisis? Responde solo con un listado detallado, sin el parrafo que sueles agregar al inicio y al final"
            final_prompt = first_line_promt + "\n" + datos + "\n" + columnas + "\n" + question

            self.upload_logcat("Realizando análisis de datos ...")
            # Create the QProgressDialog
            self.progress_dialog = QProgressDialog("Realizando análisis...", "Cancelar", 0, 0)
            self.progress_dialog.setWindowModality(2)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setWindowTitle("Consulta a GPT")
            self.progress_dialog.setFixedWidth(300)
            self.progress_dialog.hide()
            # Start the GPT analysis in a separate thread
            self.analysis_thread = GPTAnalysisThread(final_prompt)
            self.analysis_thread.analysis_completed.connect(self.analysis_completed)

            # Disable the analyze button and show the progress dialog
            self.analyze_button.setEnabled(False)
            self.progress_dialog.show()

            self.analysis_thread.start()
            #self.upload_logcat("Realizando analisis de datos ...")
            #response = analyse_gpt(final_promt)
            #self.text_area.setPlainText(response["choices"][0]['message']['content'])
        except Exception as e:
            print(f"Error al cargar el archivo: {str(e)}")
            self.upload_logcat("Error al analizar los datos: " + {str(e)})

    def analysis_completed(self, response):
        # Hide the progress dialog
        self.progress_dialog.hide()
        # Update the text area with the analysis result
        self.text_area.setPlainText(response)
        # Enable the analyze button
        self.analyze_button.setEnabled(True)
        self.upload_logcat("Análisis completado")


def main():
    app = QApplication(sys.argv)
    window = ChartApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
