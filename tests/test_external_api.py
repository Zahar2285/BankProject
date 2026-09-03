from unittest.mock import patch

from src.external_api import convert_to_rub


@patch("src.external_api.os.getenv", return_value="test_api_key")
@patch("src.external_api.requests.get")
def test_convert_usd(mock_get, mock_getenv):
    mock_get.return_value.json.return_value = {
        "rates": {
            "RUB": 91.0
        }
    }

    transaction = {
        "operationAmount": {
            "amount": "100",
            "currency": {
                "code": "USD"
            }
        }
    }

    assert convert_to_rub(transaction) == 9100.0
