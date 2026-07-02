import pytest

from src.decorators import log


@log()
def add(a, b):
    return a + b


@log()
def divide(a, b):
    return a / b


def test_log_console_success(capsys):
    assert add(2, 3) == 5

    captured = capsys.readouterr()

    assert "add ok" in captured.out


def test_log_console_error(capsys):
    with pytest.raises(ZeroDivisionError):
        divide(4, 0)

    captured = capsys.readouterr()

    assert "divide error" in captured.out
    assert "Inputs: (4, 0), {}" in captured.out


def test_log_file_success(tmp_path):
    log_file = tmp_path / "log.txt"

    @log(filename=str(log_file))
    def multiply(a, b):
        return a * b

    assert multiply(3, 4) == 12

    assert "multiply ok" in log_file.read_text(encoding="utf-8")


def test_log_file_error(tmp_path):
    log_file = tmp_path / "log.txt"

    @log(filename=str(log_file))
    def division(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        division(5, 0)

    text = log_file.read_text(encoding="utf-8")

    assert "division error" in text
    assert "Inputs: (5, 0), {}" in text
