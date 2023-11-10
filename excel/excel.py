import pandas as pd


def read_excel(excel_path):
    try:
        df = pd.read_excel(excel_path)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def clean_data(df):
    try:
        temp_df = df
        temp_df.dropna(inplace=True)  # Eliminar filas con valores NaN
        temp_df.drop_duplicates(inplace=True)  # Eliminar filas duplicadas
        return temp_df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def create_excel_file(df):
    try:
        df.to_excel('clean_data.xlsx', index=False)
        return 'Excel file created'
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return 'Error creating Excel file'
