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

        if report_date.hour == 0 and report_date.minute == 0:
            end_date = report_date + pd.Timedelta(days=1) - pd.Timedelta(
                nanoseconds=1
            )
        else:
            end_date = report_date

    dataframe = transactions.copy()

    if "Дата операции" in dataframe.columns:
        dataframe["date"] = pd.to_datetime(
            dataframe["Дата операции"],
            dayfirst=True,
            utc=True,
        )
        dataframe["amount"] = pd.to_numeric(
            dataframe["Сумма операции"],
            errors="coerce",
        )
    else:
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
        & (dataframe["date"] <= end_date)
        & (dataframe["amount"] < 0)
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

    if "Категория" in dataframe.columns:
        result: pd.DataFrame = dataframe.loc[
            dataframe["Категория"].astype(str).str.lower()
            == category.lower()
        ].copy()
    elif "description" in dataframe.columns:
        result = dataframe.loc[
            dataframe["description"].astype(str).str.lower()
            == category.lower()
        ].copy()
    else:
        result = pd.DataFrame()

    return result


@report("report_weekday.txt")
def spending_by_weekday(
    transactions: pd.DataFrame,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует средние траты по дням недели."""

    dataframe = _prepare_transactions(transactions, date)

    dataframe["weekday"] = dataframe["date"].dt.day_name()
    dataframe["amount"] = dataframe["amount"].abs()

    result: pd.DataFrame = pd.DataFrame(
        dataframe.groupby("weekday")["amount"].sum()
    ).reset_index()

    result["amount"] = result["amount"].round(2)

    return result


@report("report_weekend.txt")
def spending_by_workday(
    transactions: pd.DataFrame,
    date: str | None = None,
) -> pd.DataFrame:
    """Формирует средние траты в рабочие и выходные дни."""

    dataframe = _prepare_transactions(transactions, date)

    dataframe["day_type"] = dataframe["date"].dt.weekday.map(
        lambda day: (
            "Рабочий день"
            if day < 5
            else "Выходной день"
        )
    )

    dataframe["amount"] = dataframe["amount"].abs()

    result: pd.DataFrame = pd.DataFrame(
        dataframe.groupby("day_type")["amount"].mean()
    ).reset_index()

    result["amount"] = result["amount"].round(2)

    return result
