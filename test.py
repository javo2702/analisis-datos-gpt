import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        global df
        df = pd.read_excel(file_path)
        update_column_combos()

def update_column_combos():
    combo_x['values'] = df.columns
    combo_y['values'] = df.columns

def generate_chart():
    selected_column_x = combo_x.get()
    selected_column_y = combo_y.get()
    chart_type = combo_chart.get()

    if chart_type == 'Scatter':
        fig, ax = plt.subplots()
        ax.scatter(df[selected_column_x], df[selected_column_y])
        ax.set_xlabel(selected_column_x)
        ax.set_ylabel(selected_column_y)
        ax.set_title('Scatter Plot')
    elif chart_type == 'Bar':
        fig, ax = plt.subplots()
        ax.bar(df[selected_column_x], df[selected_column_y])
        ax.set_xlabel(selected_column_x)
        ax.set_ylabel(selected_column_y)
        ax.set_title('Bar Chart')

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

# Crear la ventana principal
root = tk.Tk()
root.title('Generador de Gráficos desde Excel')

# Botón para abrir un archivo Excel
open_button = ttk.Button(root, text='Abrir Excel', command=browse_file)
open_button.pack()

# Crear frames para la selección de columnas y gráfico
column_frame = ttk.Frame(root)
column_frame.pack()

chart_frame = ttk.Frame(root)
chart_frame.pack()

# Combobox para seleccionar la columna X
ttk.Label(column_frame, text='Selecciona la columna X:').pack()
combo_x = ttk.Combobox(column_frame)
combo_x.pack()

# Combobox para seleccionar la columna Y
ttk.Label(column_frame, text='Selecciona la columna Y:').pack()
combo_y = ttk.Combobox(column_frame)
combo_y.pack()

# Combobox para seleccionar el tipo de gráfico
ttk.Label(root, text='Selecciona el tipo de gráfico:').pack()
combo_chart = ttk.Combobox(root, values=['Scatter', 'Bar'])
combo_chart.pack()

# Botón para generar el gráfico
generate_button = ttk.Button(root, text='Generar Gráfico', command=generate_chart)
generate_button.pack()

root.mainloop()
