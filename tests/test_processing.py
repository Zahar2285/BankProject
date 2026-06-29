from src.processing import filter_by_state, sort_by_date


def test_filter_by_state_default(operations):
    result = filter_by_state(operations)

    assert len(result) == 2
    assert all(item["state"] == "EXECUTED" for item in result)


def test_filter_by_state_canceled(operations):
    result = filter_by_state(operations, "CANCELED")

    assert len(result) == 2
    assert all(item["state"] == "CANCELED" for item in result)


def test_filter_by_state_empty(operations):
    assert filter_by_state(operations, "NEW") == []


def test_sort_by_date_desc(operations):
    result = sort_by_date(operations)

    assert result[0]["date"] > result[-1]["date"]


def test_sort_by_date_asc(operations):
    result = sort_by_date(operations, False)

    assert result[0]["date"] < result[-1]["date"]
