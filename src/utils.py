import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    "logs/utils.log",
    mode="w",
    encoding="utf-8",
)

file_formatter = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
)

file_handler.setFormatter(file_formatter)

if not logger.handlers:
    logger.addHandler(file_handler)


def load_transactions(path: str) -> list[dict]:
    """
    Загружает список транзакций из JSON-файла.
    """

    logger.debug("Попытка загрузить файл: %s", path)

    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                logger.info(
                    "Файл успешно загружен. Количество транзакций: %d",
                    len(data),
                )
                return data

            logger.error("Содержимое файла не является списком.")
            return []

    except FileNotFoundError:
        logger.error("Файл не найден: %s", path)
        return []

    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON: %s", path)
        return []
