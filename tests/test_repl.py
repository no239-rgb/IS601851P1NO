from unittest.mock import MagicMock, patch
from colorama import Fore
import pytest
from decimal import Decimal
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import (
    CalculateCommand,
    ClearCommand,
    CommandDecorator,
    CommandInvoker,
    DynamicHelpDecorator, 
    HelpCommand,
    HistoryCommand,
    LoadCommand,
    RedoCommand,
    SaveCommand,
    UndoCommand,
    calculator_repl,
)
from app.exceptions import OperationError
from app.operations import Addition

def test_repl_commands_execution():
    """
    Verify individual Command objects function correctly with Invoker.
    """
    calc = Calculator()
    invoker = CommandInvoker()

    # Calculate Command
    calc_cmd = CalculateCommand(calc, "add", "10", "5")
    assert "Result: 15" in invoker.execute_command(calc_cmd)

    # History Command
    hist_cmd = HistoryCommand(calc)
    assert "10" in invoker.execute_command(hist_cmd)

    # Undo Command
    undo_cmd = UndoCommand(calc)
    assert "Undo successful" in invoker.execute_command(undo_cmd)

    # Redo Command
    redo_cmd = RedoCommand(calc)
    assert "Redo successful" in invoker.execute_command(redo_cmd)

    # Clear Command
    clear_cmd = ClearCommand(calc)
    assert "History cleared" in invoker.execute_command(clear_cmd)

    # Help Command (Decorated)
    help_cmd = DynamicHelpDecorator(HelpCommand())
    assert "Available commands" in invoker.execute_command(help_cmd)

def test_repl_calculate_command_non_decimal_result():
    """
    Verify CalculateCommand formatting when perform_operation returns non-Decimal.
    """

    calc = Calculator()
    invoker = CommandInvoker()

    with patch.object(calc, "perform_operation", return_value="15.0"):
        cmd = CalculateCommand(calc, "add", "10", "5")
        assert "Result: 15.0" in invoker.execute_command(cmd)

def test_repl_empty_history_command():
    """
    Verify HistoryCommand output when history is empty.
    """
    calc = Calculator()
    invoker = CommandInvoker()
    assert "History is empty." in invoker.execute_command(HistoryCommand(calc))

def test_repl_save_and_load_commands(tmp_path):
    """
    Verify SaveCommand and LoadCommand execution.
    """

    csv_file = str(tmp_path / "repl_history.csv")
    calc = Calculator()
    calc.set_operation(Addition())
    calc.perform_operation("2", "3")
    invoker = CommandInvoker()

    assert "saved successfully" in invoker.execute_command(SaveCommand(calc, csv_file))

    new_calc = Calculator()
    assert "loaded successfully" in invoker.execute_command(LoadCommand(new_calc, csv_file))
    assert len(new_calc.get_history()) == 1

def test_calculator_repl_full_interactive_flow(monkeypatch, capsys):
    """
    Verify standard CLI interactive input/output REPL flow.
    """

    inputs = iter([
        "help",
        "add", "10", "20",
        "undo",
        "redo",
        "history",
        "clear",
        "save",
        "load",
        "invalid_cmd",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calculator_repl()
    captured = capsys.readouterr().out

    assert "Calculator started" in captured
    assert "Available commands:" in captured
    assert "Result: 30" in captured
    assert "Undo successful." in captured
    assert "Redo successful." in captured
    assert "History cleared." in captured
    assert "Unknown command: 'invalid_cmd'" in captured
    assert "Goodbye!" in captured

def test_calculator_repl_cancel_second_operand(monkeypatch, capsys):
    """
    Verify cancellation when user enters 'cancel' on second operand prompt.
    """

    inputs = iter(["add", "10", "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calculator_repl()
    captured = capsys.readouterr().out

    assert "Operation cancelled" in captured

@patch("app.calculator_repl.Logger.error")
def test_calculator_repl_catches_operation_and_generic_errors(mock_logger_error, monkeypatch, capsys):
    """
    Verify REPL catches OperationError and logs it to Logger.error.
    """
    inputs = iter([
        "add", "10", "0",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with patch("app.calculator_repl.CalculateCommand.execute", side_effect=OperationError("Division by zero")):
        calculator_repl()

    captured = capsys.readouterr().out
    assert "Error: Division by zero" in captured
    mock_logger_error.assert_called_with("Calculation error: Division by zero")


@patch("app.calculator_repl.Logger.error")
def test_calculator_repl_catches_generic_loop_exception(mock_logger_error, monkeypatch, capsys):
    """
    Verify REPL catches unexpected generic exceptions inside loop and logs to Logger.error.
    """
    inputs = iter(["undo", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with patch("app.calculator_repl.UndoCommand.execute", side_effect=RuntimeError("System crash")):
        calculator_repl()

    captured = capsys.readouterr().out
    assert "Error: System crash" in captured
    mock_logger_error.assert_called_with("Unexpected REPL error: System crash")


def test_calculator_repl_interrupt_and_eof(monkeypatch, capsys):
    """
    Verify graceful handling of KeyboardInterrupt and EOFError.
    """

    # Test KeyboardInterrupt then exit
    inputs_interrupt = iter(["add", "exit"])
    
    def mock_input(_):
        val = next(inputs_interrupt)
        if val == "add":
            raise KeyboardInterrupt()
        return val

    monkeypatch.setattr("builtins.input", mock_input)
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Operation cancelled" in captured

    # Test EOFError
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError()))
    calculator_repl()
    captured = capsys.readouterr().out
    assert "Input terminated. Exiting..." in captured

@patch("app.calculator_repl.Logger.error")
def test_calculator_repl_fatal_initialization_error(mock_logger_error):
    """
    Verify fatal startup exception during calculator REPL setup is logged and re-raised.
    """
    with patch("app.calculator_repl.Calculator", side_effect=RuntimeError("Fatal init failed")):
        with pytest.raises(RuntimeError, match="Fatal init failed"):
            calculator_repl()
            
    mock_logger_error.assert_called_with("Fatal REPL error: Fatal init failed")


def test_calculator_repl_cancel_first_number_prompt(monkeypatch, capsys):
    """
    Verify entering 'cancel' at the first number prompt prints cancellation message and continues the loop.
    """

    inputs = iter(["add", "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calculator_repl()
    captured = capsys.readouterr().out

    assert "Operation cancelled" in captured
    assert "Goodbye!" in captured

def test_calculator_repl_cancel_second_number_prompt(monkeypatch, capsys):
    """
    Verify entering 'cancel' at the second number prompt prints cancellation message and continues the loop.
    """

    inputs = iter(["add", "10", "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calculator_repl()
    captured = capsys.readouterr().out

    assert "Operation cancelled" in captured
    assert "Goodbye!" in captured

def test_repl_calculate_command_applies_configured_precision():
    """Verify CalculateCommand formats calculation output using CalculatorConfig.precision."""
    config = CalculatorConfig(precision=2)
    calc = Calculator(config)
    invoker = CommandInvoker()

    # 10 / 3 = 3.3333333333... -> with precision=2, format_result should yield "3.33"
    cmd = CalculateCommand(calc, "divide", "10", "3")
    result = invoker.execute_command(cmd)

    assert "Result: 3.33" in result

def test_repl_calculate_command_mocked_decimal_result():
    """
    Verify CalculateCommand fallback formatting when perform_operation returns a Decimal 
    and history is not populated.
    """
    calc = Calculator()
    invoker = CommandInvoker()

    with patch.object(calc, "perform_operation", return_value=Decimal("15.00")):
        cmd = CalculateCommand(calc, "add", "10", "5")
        assert "Result: 15" in invoker.execute_command(cmd)

def test_dynamic_help_decorator_pattern():
    """Verify DynamicHelpDecorator correctly wraps HelpCommand using Decorator Design Pattern."""
    base_help = HelpCommand()
    decorated_help = DynamicHelpDecorator(base_help)

    invoker = CommandInvoker()
    output = invoker.execute_command(decorated_help)

    assert "Available commands:" in output
    assert "Perform calculations" in output
    assert "history - Display calculation history" in output
    assert Fore.CYAN in output or Fore.GREEN in output  # Verify colorama integration


def test_dynamic_help_decorator_reflects_registered_operations():
    """Verify dynamic help updates automatically when a new operation is registered in OperationFactory."""
    from app.operations import OperationFactory, Addition

    class CustomModOperation(Addition):
        pass

    OperationFactory.register_operation("custom_test_op", CustomModOperation)

    decorated_help = DynamicHelpDecorator(HelpCommand())
    invoker = CommandInvoker()
    output = invoker.execute_command(decorated_help)

    assert "custom_test_op" in output

def test_base_command_decorator_execute():
    """Verify base CommandDecorator delegates execute() to wrapped command."""
    base_cmd = HelpCommand()
    decorator = CommandDecorator(base_cmd)

    # Asserts that CommandDecorator.execute() delegates directly to base_cmd.execute()
    assert decorator.execute() == base_cmd.execute()