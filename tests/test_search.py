from src.search import process_bank_operations, process_bank_search


def test_process_bank_search() -> None:
    data = [
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
        {"description": "Перевод с карты на карту"},
    ]

    assert process_bank_search(data, "перевод") == [
        {"description": "Перевод организации"},
        {"description": "Перевод с карты на карту"},
    ]


def test_process_bank_search_empty_result() -> None:
    data = [{"description": "Открытие вклада"}]
    assert process_bank_search(data, "перевод") == []


def test_process_bank_operations() -> None:
    data = [
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
        {"description": "Перевод организации"},
    ]

    assert process_bank_operations(
        data,
        [
            "Перевод организации",
            "Открытие вклада",
            "Перевод с карты на карту",
        ],
    ) == {
        "Перевод организации": 2,
        "Открытие вклада": 1,
        "Перевод с карты на карту": 0,
    }
