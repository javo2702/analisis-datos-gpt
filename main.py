# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from excel.excel import read_excel
from excel.excel import clean_data
from excel.excel import create_excel_file
from util.functions import loading

from gpt.functions import ask_gpt
from ui.home import paint_ui


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    paint_ui()
    # path = 'reporte.xlsx'
    # dataframe = read_excel(path)
    # Verifica si se pudo cargar el DataFrame correctamente
    # if dataframe is not None:
        # print(dataframe.head())
        # clean_df = clean_data(dataframe)
        # print(f"------------------------------")
        # print(clean_df.head())
        # result = loading(create_excel_file, 'Creating Excel File', clean_df)
        # print(f"{result}")
        # api_key = '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'
        # result = ask_gpt(
            # "¿Puedes proporcionar un analisis de los siguientes datos?",
            # api_key,
            # clean_df
        # )
        # print(f"{result}")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
