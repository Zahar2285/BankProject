import pandas as pd


def read_csv(path: str) -> list[dict]:
    """
    Считывает финансовые операции из CSV-файла.

    Args:
        path: Путь к CSV-файлу.

    Returns:
        Список словарей с транзакциями.
    """
    dataframe = pd.read_csv(path)
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
