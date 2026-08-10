from unittest.mock import MagicMock, patch

from src.readers import read_csv, read_excel


@patch("src.readers.pd.read_csv")
def test_read_csv(mock_read_csv):
    dataframe = MagicMock()
    dataframe.to_dict.return_value = [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200},
    ]

    mock_read_csv.return_value = dataframe

    result = read_csv("transactions.csv")

    assert result == [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200},
    ]
    mock_read_csv.assert_called_once_with("transactions.csv")


@patch("src.readers.pd.read_excel")
def test_read_excel(mock_read_excel):
    dataframe = MagicMock()
    dataframe.to_dict.return_value = [
        {"id": 1, "amount": 500},
    ]

    mock_read_excel.return_value = dataframe

    result = read_excel("transactions.xlsx")

    assert result == [
        {"id": 1, "amount": 500},
    ]
    mock_read_excel.assert_called_once_with("transactions.xlsx")
