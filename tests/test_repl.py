from decimal import Decimal
import pytest

from app.calculator_repl import calculator_repl
from app.exceptions import ValidationError


def test_repl_help_command(monkeypatch, capsys):
    """Verify that 'help' displays all available operations and options."""
    inputs = iter(["help", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Available commands:" in captured
    assert "add, subtract, multiply, divide, power, root, modulus, integer_division, absolute_difference, percentage" in captured
    assert "Goodbye!" in captured


@pytest.mark.parametrize(
    "command, val_a, val_b, expected_output",
    [
        ("add", "10", "5", "Result: 15"),
        ("subtract", "10", "4", "Result: 6"),
        ("multiply", "3", "4", "Result: 12"),
        ("divide", "20", "5", "Result: 4"),
        ("power", "2", "3", "Result: 8"),
        ("root", "16", "2", "Result: 4"),
        ("modulus", "10", "3", "Result: 1"),
        ("integer_division", "10", "3", "Result: 3"),
        ("absolute_difference", "5", "12", "Result: 7"),
        ("percentage", "25", "100", "Result: 25"),
    ],
)
def test_repl_successful_operations(monkeypatch, capsys, command, val_a, val_b, expected_output):
    """Verify execution of all supported arithmetic operations through the REPL loop."""
    inputs = iter([command, val_a, val_b, "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    calculator_repl()

    captured = capsys.readouterr().out
    assert expected_output in captured


def test_repl_decimal_result_normalization_true_branch(monkeypatch, capsys):
    """
    Verify the True branch: When perform_operation returns a Decimal,
    it is normalized and formatted as a standard fixed-point string.
    """
    inputs = iter(["add", "5", "5", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    monkeypatch.setattr(
        "app.calculator_repl.Calculator.perform_operation",
        lambda self, a, b: Decimal("10.5000"),
    )

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Result: 10.5" in captured


def test_repl_decimal_result_normalization_false_branch(monkeypatch, capsys):
    """
    Verify the False branch: When perform_operation returns a non-Decimal (e.g. str),
    isinstance evaluates to False and skips normalization without error.
    """
    inputs = iter(["add", "5", "5", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    monkeypatch.setattr(
        "app.calculator_repl.Calculator.perform_operation",
        lambda self, a, b: "42",
    )

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Result: 42" in captured


@pytest.mark.parametrize("cancel_input", ["cancel", "CANCEL", "Cancel"])
def test_repl_cancel_operation_first_number(monkeypatch, capsys, cancel_input):
    """Verify aborting an operation when 'cancel' is entered for the first operand."""
    inputs = iter(["add", cancel_input, "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Operation cancelled" in captured


@pytest.mark.parametrize("cancel_input", ["cancel", "CANCEL", "Cancel"])
def test_repl_cancel_operation_second_number(monkeypatch, capsys, cancel_input):
    """Verify aborting an operation when 'cancel' is entered for the second operand."""
    inputs = iter(["multiply", "10", cancel_input, "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Operation cancelled" in captured


def test_repl_validation_error_handling(monkeypatch, capsys):
    """Verify catching and printing known ValidationError during execution (e.g., division by zero)."""
    inputs = iter(["divide", "10", "0", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Error: Division by zero is not allowed" in captured


def test_repl_unexpected_operation_exception(monkeypatch, capsys):
    """Verify unexpected non-validation exceptions inside the operation block are caught and printed."""
    inputs = iter(["add", "10", "5", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    def mock_perform_operation(self, a, b):
        raise RuntimeError("Operation engine malfunction")

    monkeypatch.setattr("app.calculator.Calculator.perform_operation", mock_perform_operation)

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Unexpected error: Operation engine malfunction" in captured


def test_repl_unknown_command(monkeypatch, capsys):
    """Verify handling of unrecognized commands."""
    inputs = iter(["foobar", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Unknown command: 'foobar'. Type 'help' for available commands." in captured


def test_repl_keyboard_interrupt(monkeypatch, capsys):
    """Verify graceful handling of KeyboardInterrupt (Ctrl+C)."""
    calls = 0

    def mock_input(prompt=""):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise KeyboardInterrupt()
        return "exit"

    monkeypatch.setattr("builtins.input", mock_input)

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Operation cancelled" in captured
    assert "Goodbye!" in captured


def test_repl_eof_error(monkeypatch, capsys):
    """Verify graceful handling of EOFError (Ctrl+D)."""
    monkeypatch.setattr("builtins.input", lambda prompt="": (_ for _ in ()).throw(EOFError()))

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Input terminated. Exiting..." in captured


def test_repl_main_loop_generic_exception(monkeypatch, capsys):
    """Verify catching generic exceptions in the inner REPL loop block."""
    calls = 0

    def mock_input(prompt=""):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("Generic loop error")
        return "exit"

    monkeypatch.setattr("builtins.input", mock_input)

    calculator_repl()

    captured = capsys.readouterr().out
    assert "Error: Generic loop error" in captured


def test_repl_fatal_initialization_error(monkeypatch, capsys):
    """Verify fatal initialization errors outside the main loop are logged and re-raised."""

    def mock_init(self):
        raise RuntimeError("Database/Config init failure")

    monkeypatch.setattr("app.calculator.Calculator.__init__", mock_init)

    with pytest.raises(RuntimeError, match="Database/Config init failure"):
        calculator_repl()

    captured = capsys.readouterr().out
    assert "Fatal error: Database/Config init failure" in captured