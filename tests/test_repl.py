from unittest.mock import patch
import pytest
from decimal import Decimal
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError


@pytest.fixture
def run_repl(monkeypatch, capsys):
    """
    Test harness fixture that feeds simulated user inputs into calculator_repl()
    and captures all printed standard output.
    """
    def _execute(inputs):
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda prompt="": next(input_iter))
        calculator_repl()
        return capsys.readouterr().out

    return _execute


@pytest.mark.parametrize(
    "inputs, expected_snippets",
    [
        (["help", "exit"], ["Available commands:", "Goodbye!"]),
        (["exit"], ["Calculator started.", "Goodbye!"]),
        (["invalid_cmd", "exit"], ["Unknown command: 'invalid_cmd'.", "Goodbye!"]),
        (["add", "cancel", "exit"], ["Operation cancelled"]),
        (["add", "10", "cancel", "exit"], ["Operation cancelled"]),
        (["add", "2", "3", "exit"], ["Result: 5"]),
        (["subtract", "10", "4", "exit"], ["Result: 6"]),
        (["multiply", "2.5", "4", "exit"], ["Result: 10"]),
        (["divide", "20", "5", "exit"], ["Result: 4"]),
        (["power", "2", "3", "exit"], ["Result: 8"]),
        (["root", "16", "2", "exit"], ["Result: 4"]),
    ],
)
def test_repl_commands_and_operations(run_repl, inputs, expected_snippets):
    """Test commands, cancellations, and valid arithmetic operations in a single harness."""
    output = run_repl(inputs)
    for snippet in expected_snippets:
        assert snippet in output


@pytest.mark.parametrize(
    "inputs, side_effect, expected_snippet",
    [
        (
            ["add", "10", "abc", "exit"],
            ValidationError("Invalid number format"),
            "Error: Invalid number format",
        ),
        (
            ["add", "10", "0", "exit"],
            OperationError("Division by zero is not allowed"),
            "Error: Division by zero is not allowed",
        ),
        (
            ["add", "5", "5", "exit"],
            RuntimeError("Unexpected error"),
            "Unexpected error: Unexpected error",
        ),
    ],
)
@patch("app.calculator_repl.Calculator.perform_operation")
def test_repl_operation_exceptions(mock_perform, run_repl, inputs, side_effect, expected_snippet):
    """Test handling of ValidationError, OperationError, and generic exceptions during calculation."""
    mock_perform.side_effect = side_effect
    output = run_repl(inputs)
    assert expected_snippet in output


def test_repl_keyboard_interrupt(monkeypatch, capsys):
    """Test handling of KeyboardInterrupt (Ctrl+C) during input prompt."""
    calls = 0

    def mock_input(prompt=""):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise KeyboardInterrupt()
        return "exit"

    monkeypatch.setattr("builtins.input", mock_input)
    calculator_repl()

    output = capsys.readouterr().out
    assert "Operation cancelled" in output
    assert "Goodbye!" in output


def test_repl_eof_interrupt(monkeypatch, capsys):
    """Test handling of EOFError (Ctrl+D) gracefully exiting the REPL."""
    monkeypatch.setattr("builtins.input", lambda prompt="": (_ for _ in ()).throw(EOFError()))
    calculator_repl()

    output = capsys.readouterr().out
    assert "Input terminated. Exiting..." in output


@patch("app.calculator_repl.Calculator", side_effect=Exception("Initialization failed"))
def test_repl_fatal_initialization_error(mock_calc, capsys):
    """Test fatal error during calculator initialization prints message and re-raises exception."""
    with pytest.raises(Exception, match="Initialization failed"):
        calculator_repl()

    captured = capsys.readouterr().out
    assert "Fatal error: Initialization failed" in captured

@pytest.mark.parametrize(
    "cmd, a, b, perform_return, expected_output",
    [
        # Converts scientific notation (10.00 -> 1E+1 -> "10")
        ("multiply", "2.5", "4", Decimal("10.00"), "Result: 10"),
        # Removes trailing zeros (12.3400 -> "12.34")
        ("add", "10.000", "2.3400", Decimal("12.3400"), "Result: 12.34"),
        # Normalizes zero values (0.000 -> "0")
        ("subtract", "5.0", "5.0", Decimal("0.000"), "Result: 0"),
        # Passes non-Decimal results through cleanly
        ("add", "1", "2", "Non-Decimal Result", "Result: Non-Decimal Result"),
    ],
)
@patch("app.calculator_repl.Calculator.perform_operation")
def test_repl_decimal_result_formatting(mock_perform, run_repl, cmd, a, b, perform_return, expected_output):
    """
    Verify that Decimal results are normalized to remove trailing zeros
    and formatted with fixed-point notation (:f) to avoid scientific notation.
    """
    mock_perform.return_value = perform_return
    output = run_repl([cmd, a, b, "exit"])
    assert expected_output in output

def test_repl_main_loop_generic_exception(monkeypatch, capsys):
    """
    Verify that unexpected non-interrupt exceptions raised during command processing 
    in the main REPL loop are caught, printed as 'Error: <message>', and allow the loop to continue.
    """
    calls = 0

    def mock_input(prompt=""):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("Unexpected main loop failure")
        return "exit"

    monkeypatch.setattr("builtins.input", mock_input)
    calculator_repl()

    captured = capsys.readouterr().out
    assert "Error: Unexpected main loop failure" in captured
    assert "Goodbye!" in captured