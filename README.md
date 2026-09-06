# Банковский виджет

## Описание проекта

Проект предназначен для обработки банковских операций клиента.

Реализованы функции:

* маскировка номеров банковских карт;
* маскировка номеров счетов;
* определение типа платежного инструмента;
* преобразование даты из ISO-формата;
* фильтрация операций по статусу;
* сортировка операций по дате.

## Установка

Клонируйте репозиторий:

```bash
git clone <ссылка-на-репозиторий>
```

Перейдите в директорию проекта:

```bash
cd project
```

## Использование

### Фильтрация операций

```python
from src.processing import filter_by_state

result = filter_by_state(operations)
```

### Сортировка операций

```python
from src.processing import sort_by_date

result = sort_by_date(operations)
```

### Маскировка карты или счета

```python
from src.widget import mask_account_card

print(mask_account_card("Visa Platinum 7000792289606361"))
```

## Тестирование

Для запуска тестов выполните:

```bash
pytest
```

Для получения отчета о покрытии:

```bash
pytest --cov=src --cov-report=html
```

После выполнения будет создан каталог `htmlcov` с HTML-отчетом о покрытии кода тестами.

Для проверки качества кода:

```bash
flake8 .
mypy src
```

### Модуль `generators`

Проект содержит модуль `generators`, предназначенный для обработки транзакций с помощью генераторов.

#### `filter_by_currency()`

Возвращает только транзакции с указанной валютой.

```python
from src.generators import filter_by_currency

usd_transactions = filter_by_currency(transactions, "USD")

for transaction in usd_transactions:
    print(transaction)
```

#### `transaction_descriptions()`

Последовательно возвращает описания операций.

```python
from src.generators import transaction_descriptions

for description in transaction_descriptions(transactions):
    print(description)
```

#### `card_number_generator()`

Генерирует номера банковских карт в формате `XXXX XXXX XXXX XXXX`.

```python
from src.generators import card_number_generator

for number in card_number_generator(1, 5):
    print(number)
```
## Модуль decorators

В проект добавлен модуль `decorators`, содержащий декоратор `log`.

### Пример использования

```python
from src.decorators import log


@log()
def add(a, b):
    return a + b


add(2, 3) 
```
    

## Поиск и подсчет операций

### Поиск по описанию

Функция `process_bank_search()` использует регулярные выражения и возвращает операции, в описании которых встречается заданная строка.

### Подсчет операций по категориям

Функция `process_bank_operations()` использует `Counter` для подсчета количества операций по категориям из поля `description`.

## Консольное приложение

Функция `main()` объединяет загрузку данных из JSON, CSV и XLSX, фильтрацию по статусу, сортировку по дате, фильтрацию рублевых операций и поиск по описанию.

Для запуска программы выполните:

```bash
python main.py
```

## Новые возможности

### load_transactions(path)

Читает JSON-файл и возвращает список транзакций.

### convert_to_rub(transaction)

Конвертирует сумму операции в рубли через Exchange Rates Data API.

## Пример

```python
from src.utils import load_transactions
from src.external_api import convert_to_rub

transactions = load_transactions("data/operations.json")

print(convert_to_rub(transactions[0]))
```

### Автор

Александр Захаров
