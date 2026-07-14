import os

import requests
from dotenv import load_dotenv

load_dotenv()


def convert_to_rub(transaction: dict) -> float:
    """
    Возвращает сумму операции в рублях.
    """

    amount = float(transaction["operationAmount"]["amount"])
    currency = transaction["operationAmount"]["currency"]["code"]

    if currency == "RUB":
        return amount

    api_key = os.getenv("API_KEY")

    response = requests.get(
        "https://api.apilayer.com/exchangerates_data/latest",
        headers={"apikey": api_key},
        params={
            "base": currency,
            "symbols": "RUB",
        },
        timeout=10,
    )

    rate = response.json()["rates"]["RUB"]

    return amount * rate
