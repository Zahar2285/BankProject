import pytest

from src.generators import (
    card_number_generator,
    filter_by_currency,
    transaction_descriptions,
)


def test_filter_by_currency(transactions):
    result = list(filter_by_currency(transactions, "USD"))

    assert len(result) == 2
    assert all(
        item["operationAmount"]["currency"]["code"] == "USD"
        for item in result
    )


def test_filter_by_currency_empty(transactions):
    assert list(filter_by_currency(transactions, "EUR")) == []


def test_transaction_descriptions(transactions):
    result = list(transaction_descriptions(transactions))

    assert result == [
        "Перевод организации",
        "Оплата",
        "Перевод со счета",
    ]


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (
            1,
            3,
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
            ],
        ),
        (
            9998,
            10000,
            [
                "0000 0000 0000 9998",
                "0000 0000 0000 9999",
                "0000 0000 0001 0000",
            ],
        ),
    ],
)
def test_card_number_generator(start, stop, expected):
    assert list(card_number_generator(start, stop)) == expected


def test_card_number_generator_empty():
    assert list(card_number_generator(5, 4)) == []
