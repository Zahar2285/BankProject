import pandas as pd


def read_csv_file(file_path: str) -> list[dict]:
    """Считывает транзакции из CSV-файла и возвращает список словарей."""
    dataframe = pd.read_csv(file_path, sep=";")
    return dataframe.to_dict(orient="records")

def read_excel(path: str) -> list[dict]:
    """
    Считывает финансовые операции из Excel-файла.

    Args:
        path: Путь к Excel-файлу.

    Returns:
        Список словарей с транзакциями.
    """
    dataframe = pd.read_excel(path)
    return dataframe.to_dict(orient="records")
