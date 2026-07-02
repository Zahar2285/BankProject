from collections.abc import Callable
from functools import wraps
from typing import Any


def log(filename: str | None = None) -> Callable:
    """
    Декоратор для логирования работы функций.

    Если filename не указан, лог выводится в консоль.
    Если указан, лог записывается в файл.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                message = f"{func.__name__} ok"

                if filename:
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(message + "\n")
                else:
                    print(message)

                return result

            except Exception as error:
                message = (
                    f"{func.__name__} error: {error}. "
                    f"Inputs: {args}, {kwargs}"
                )

                if filename:
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(message + "\n")
                else:
                    print(message)

                raise

        return wrapper

    return decorator