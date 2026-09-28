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
                "description": "Супермаркеты",
                "amount": -100.50,
                "date": "2026-09-01T10:00:00Z",
            },
            {
                "description": "Супермаркеты",
                "amount": -200.25,
                "date": "2026-09-02T10:00:00Z",
            },
            {
                "description": "Рестораны",
                "amount": -500.00,
                "date": "2026-09-03T10:00:00Z",
            },
            {
                "description": "Супермаркеты",
                "amount": 50.00,
                "date": "2026-09-04T10:00:00Z",
            },
        ]
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
