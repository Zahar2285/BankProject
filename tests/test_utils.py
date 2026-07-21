from src.utils import load_transactions


def test_load_transactions():
    result = load_transactions("data/operations.json")

    assert isinstance(result, list)


def test_file_not_found():
    assert load_transactions("abc.json") == []