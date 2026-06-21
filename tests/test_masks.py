import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.mark.parametrize(
    "card, expected",
    [
        ("1234567812345678", "1234 56** **** 5678"),
        ("7000792289606361", "7000 79** **** 6361"),
    ],
)
def test_get_mask_card_number(card, expected):
    assert get_mask_card_number(card) == expected


def test_get_mask_card_number_error():
    with pytest.raises(ValueError):
        get_mask_card_number("123")


@pytest.mark.parametrize(
    "account, expected",
    [
        ("1234567890", "**7890"),
        ("73654108430135874305", "**4305"),
    ],
)
def test_get_mask_account(account, expected):
    assert get_mask_account(account) == expected


def test_get_mask_account_error():
    with pytest.raises(ValueError):
        get_mask_account("123")