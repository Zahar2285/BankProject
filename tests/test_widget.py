import pytest

from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "Visa Platinum 7000792289606361",
            "Visa Platinum 7000 79** **** 6361",
        ),
        (
            "Счет 73654108430135874305",
            "Счет **4305",
        ),
    ],
)
def test_mask_account_card(data, expected):
    assert mask_account_card(data) == expected


def test_mask_account_card_error():
    with pytest.raises(ValueError):
        mask_account_card("Visa")


def test_get_date():
    assert (
        get_date("2024-03-11T02:26:18.671407")
        == "11.03.2024"
    )


def test_get_date_error():
    with pytest.raises(ValueError):
        get_date("wrong date")