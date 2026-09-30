from src.views import (
    _build_cards,
    _build_top_transactions,
    _get_greeting,
    _parse_date,
)


def test_get_greeting():
    assert _get_greeting(8) == "Доброе утро"
    assert _get_greeting(14) == "Добрый день"
    assert _get_greeting(20) == "Добрый вечер"
    assert _get_greeting(2) == "Доброй ночи"


def test_parse_date():
    assert _parse_date("31.12.2021 15:30:00") is not None
    assert _parse_date("2021-12-31 15:30:00") is not None
    assert _parse_date("31.12.2021") is not None
    assert _parse_date("2021-12-31") is not None
    assert _parse_date("invalid") is None


def test_build_cards():
    data = [
        {
            "Номер карты": "*1234",
            "Сумма операции": -1000,
        },
        {
            "Номер карты": "*1234",
            "Сумма операции": -500,
        },
        {
            "Номер карты": "*5678",
            "Сумма операции": -200,
        },
    ]

    result = _build_cards(data)

    assert len(result) == 2
    assert result[0]["last_digits"] == "1234"
    assert result[0]["total_spent"] == 1500
    assert result[0]["cashback"] == 15


def test_build_top_transactions():
    data = [
        {
            "Дата операции": "01.12.2021 10:00:00",
            "Сумма операции": -500,
            "Категория": "Продукты",
            "Описание": "Магазин",
        },
        {
            "Дата операции": "02.12.2021 10:00:00",
            "Сумма операции": -1500,
            "Категория": "Одежда",
            "Описание": "Магазин одежды",
        },
    ]

    result = _build_top_transactions(data)

    assert len(result) == 2
    assert result[0]["amount"] == -1500
    assert result[0]["category"] == "Одежда"
    assert result[0]["date"] == "02.12.2021"
    