from src.views import (
    _build_cards,
    _build_top_transactions,
    _get_greeting,
    _parse_date,
)
from src.views import _build_expenses, _build_income
from datetime import datetime
from src.views import _get_events_period


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


def test_build_expenses():
        data = [
            {
                "Сумма операции": -1000,
                "Категория": "Продукты",
            },
            {
                "Сумма операции": -500,
                "Категория": "Продукты",
            },
            {
                "Сумма операции": -300,
                "Категория": "Одежда",
            },
            {
                "Сумма операции": -200,
                "Категория": "Переводы",
            },
            {
                "Сумма операции": -100,
                "Категория": "Снятие наличных",
            },
        ]

        result = _build_expenses(data)

        assert result["total_amount"] == 2100
        assert result["main"][0] == {
            "category": "Продукты",
            "amount": 1500,
        }
        assert result["transfers_and_cash"] == [
            {"category": "Переводы", "amount": 200},
            {"category": "Наличные", "amount": 100},
        ]

def test_build_income():
        data = [
            {
                "Сумма операции": 5000,
                "Категория": "Зарплата",
            },
            {
                "Сумма операции": 2000,
                "Категория": "Зарплата",
            },
            {
                "Сумма операции": 500,
                "Категория": "Кешбэк",
            },
            {
                "Сумма операции": -1000,
                "Категория": "Продукты",
            },
        ]

        result = _build_income(data)

        assert result["total_amount"] == 7500
        assert result["main"] == [
            {"category": "Зарплата", "amount": 7000},
            {"category": "Кешбэк", "amount": 500},
        ]
from src.views import _get_events_period


def test_get_events_period_week():
    current_datetime = datetime(2021, 12, 15, 12, 30, 0)

    start_date, end_date = _get_events_period(current_datetime, "W")

    assert start_date == datetime(2021, 12, 13, 0, 0, 0)
    assert end_date == current_datetime


def test_get_events_period_month():
    current_datetime = datetime(2021, 12, 15, 12, 30, 0)

    start_date, end_date = _get_events_period(current_datetime, "M")

    assert start_date == datetime(2021, 12, 1, 0, 0, 0)
    assert end_date == current_datetime


def test_get_events_period_year():
    current_datetime = datetime(2021, 12, 15, 12, 30, 0)

    start_date, end_date = _get_events_period(current_datetime, "Y")

    assert start_date == datetime(2021, 1, 1, 0, 0, 0)
    assert end_date == current_datetime