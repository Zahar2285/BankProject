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
        end_date = report_date
    else:
        report_date = pd.Timestamp(date, tz="UTC")

        # Если передана только дата, учитываем весь этот день.
        if report_date.hour == 0 and report_date.minute == 0:
            end_date = report_date + pd.Timedelta(days=1) - pd.Timedelta(
                nanoseconds=1
            )
        else:
            end_date = report_date

    dataframe = transactions.copy()

    dataframe["Дата операции"] = pd.to_datetime(
        dataframe["Дата операции"],
        dayfirst=True,
        utc=True,
    )

    dataframe["Сумма операции"] = pd.to_numeric(
        dataframe["Сумма операции"],
        errors="coerce",
    )

    start_date = report_date - pd.DateOffset(months=3)

    result: pd.DataFrame = dataframe.loc[
        (dataframe["Дата операции"] >= start_date)
        & (dataframe["Дата операции"] <= end_date)
        & (dataframe["Сумма операции"] < 0)
    ].copy()

    return result


@report()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует отчёт о тратах по указанной категории."""

    dataframe = _prepare_transactions(transactions, date)

    result = dataframe.loc[
        dataframe["Категория"].astype(str).str.lower()
        == category.lower()
    ].copy()

    result["Сумма операции"] = result["Сумма операции"].abs()

    return result


@report("report_weekday.txt")
def spending_by_weekday(
    transactions: pd.DataFrame,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует средние траты по дням недели."""

    dataframe = _prepare_transactions(transactions, date)

    dataframe["weekday"] = dataframe["Дата операции"].dt.day_name()

    dataframe["Сумма операции"] = dataframe["Сумма операции"].abs()

    result: pd.DataFrame = (
        dataframe.groupby("weekday", as_index=False)
        .agg(amount=("Сумма операции", "mean"))
    )

    result["amount"] = result["amount"].round(2)

    return result


@report("report_weekend.txt")
def spending_by_workday(
    transactions: pd.DataFrame,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует средние траты в рабочие и выходные дни."""

    dataframe = _prepare_transactions(transactions, date)

    dataframe["day_type"] = dataframe["Дата операции"].dt.weekday.map(
        lambda day: (
            "Рабочий день"
            if day < 5
            else "Выходной день"
        )
    )

    dataframe["Сумма операции"] = dataframe["Сумма операции"].abs()

    result: pd.DataFrame = (
        dataframe.groupby("day_type", as_index=False)
        .agg(amount=("Сумма операции", "mean"))
    )

    result["amount"] = result["amount"].round(2)

    return result