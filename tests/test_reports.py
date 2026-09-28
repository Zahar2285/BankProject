from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday,
)
import pandas as pd


def test_spending_by_category():
    data = pd.DataFrame(
        [
            {
                "Категория": "Супермаркеты",
                "Сумма операции": -100.50,
                "Дата операции": "01.09.2026 10:00:00",
            },
            {
                "Категория": "Супермаркеты",
                "Сумма операции": -200.25,
                "Дата операции": "02.09.2026 10:00:00",
            },
            {
                "Категория": "Рестораны",
                "Сумма операции": -500.00,
                "Дата операции": "03.09.2026 10:00:00",
            },
        ]
    )

    data = data.rename(
        columns={
            "Категория": "description",
            "Сумма операции": "amount",
            "Дата операции": "date",
        }
    )

    result = spending_by_category(
        data,
        "Супермаркеты",
        "2026-09-30",
    )

    assert len(result) == 2
    assert result["amount"].sum() == -300.75


def test_spending_by_weekday():
    data = pd.DataFrame(
        [
            {
                "date": "2026-09-01T10:00:00Z",
                "amount": -100.00,
            },
            {
                "date": "2026-09-02T10:00:00Z",
                "amount": -200.00,
            },
            {
                "date": "2026-09-01T12:00:00Z",
                "amount": -50.00,
            },
        ]
    )

    result = spending_by_weekday(
        data,
        "2026-09-30",
    )

    assert result["amount"].sum() == 350.00

def test_spending_by_workday():
    data = pd.DataFrame(
        [
            {
                "date": "2026-09-01T10:00:00Z",
                "amount": -100.00,
            },
            {
                "date": "2026-09-05T10:00:00Z",
                "amount": -200.00,
            },
        ]
    )

    result = spending_by_workday(
        data,
        "2026-09-30",
    )

    assert result["amount"].sum() == 300.00