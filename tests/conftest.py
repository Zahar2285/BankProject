import pytest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture
def operations():
    return [
        {
            "id": 41428829,
            "state": "EXECUTED",
            "date": "2019-07-03T18:35:29.512364",
        },
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
        },
        {
            "id": 615064591,
            "state": "CANCELED",
            "date": "2018-10-14T08:21:33.419441",
        },
    ]

@pytest.fixture
def transactions():
    return [
        {
            "id": 1,
            "operationAmount": {
                "currency": {"code": "USD"}
            },
            "description": "Перевод организации",
        },
        {
            "id": 2,
            "operationAmount": {
                "currency": {"code": "RUB"}
            },
            "description": "Оплата",
        },
        {
            "id": 3,
            "operationAmount": {
                "currency": {"code": "USD"}
            },
            "description": "Перевод со счета",
        },
    ]