from functools import wraps
from typing import Any, Callable

import pandas as pd


def report(filename: str = "report.txt") -> Callable:
    """Сохраняет результат отчёта в файл."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(result))

            return result

        return wrapper

    return decorator


def _prepare_transactions(
    transactions: pd.DataFrame,
    date: str | None,
) -> pd.DataFrame:
    """Подготавливает расходы за последние три месяца."""
    if date is None:
        report_date = pd.Timestamp.now(tz="UTC")
    else:
        report_date = pd.Timestamp(date, tz="UTC")

    dataframe = transactions.copy()

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        utc=True,
    )
    dataframe["amount"] = pd.to_numeric(
        dataframe["amount"],
        errors="coerce",
    )

    start_date = report_date - pd.DateOffset(months=3)

    result: pd.DataFrame = dataframe.loc[
        (dataframe["date"] >= start_date)
        & (dataframe["date"] <= report_date)
        & (dataframe["amount"] < 0)
    ]

    return result


@report()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует отчёт о тратах по категории."""
    dataframe = _prepare_transactions(transactions, date)

    result: pd.DataFrame

    if "Категория" in dataframe.columns:
        result = dataframe.loc[
            dataframe["Категория"] == category]
    else:
        result = dataframe.loc[
            dataframe["description"] == category]

    return result


@report("report_weekday.txt")
def spending_by_weekday(
    transactions: pd.DataFrame,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует отчёт о тратах по дням недели."""
    dataframe = _prepare_transactions(transactions, date)

    dataframe["weekday"] = dataframe["date"].dt.day_name()

    result: pd.DataFrame = (
        dataframe.groupby("weekday", as_index=False)
        .agg(amount=("amount", "sum"))
    )

    result["amount"] = result["amount"].abs().round(2)

    return result


@report("report_weekend.txt")
def spending_by_workday(
    transactions: pd.DataFrame,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует отчёт о тратах в рабочие и выходные дни."""
    dataframe = _prepare_transactions(transactions, date)

    dataframe["day_type"] = dataframe["date"].dt.weekday.map(
        lambda day: (
            "Рабочий день"
            if day < 5
            else "Выходной день"
        )
    )

    result: pd.DataFrame = (
        dataframe.groupby("day_type", as_index=False)
        .agg(amount=("amount", "sum"))
    )

    result["amount"] = result["amount"].abs().round(2)

    return result
