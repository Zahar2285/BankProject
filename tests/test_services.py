from src.services import (
    search_person_transfers,
    search_phone_numbers,
    simple_search,
)


def test_simple_search() -> None:
    data = [
        {"Категория": "Супермаркеты", "Описание": "Магнит"},
        {"Категория": "Рестораны", "Описание": "Кафе"},
        {"Категория": "Переводы", "Описание": "Иван Иванов"},
    ]

    assert simple_search(data, "супермаркеты") == [
        {"Категория": "Супермаркеты", "Описание": "Магнит"}
    ]


def test_search_phone_numbers() -> None:
    data = [
        {"Описание": "Я МТС +7 921 11-22-33"},
        {"Описание": "Покупка в магазине"},
    ]

    assert search_phone_numbers(data) == [
        {"Описание": "Я МТС +7 921 11-22-33"}
    ]


def test_search_person_transfers() -> None:
    data = [
        {"Категория": "Переводы", "Описание": "Переводы - Константин Л."},
        {"Категория": "Супермаркеты", "Описание": "Переводы - Дмитрий Ш."},
    ]

    assert search_person_transfers(data) == [
        {"Категория": "Переводы", "Описание": "Переводы - Константин Л."}
    ]
