from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.operations import Addition


def test_calculator_init_and_set_operation():
    """Verify calculator initialization and operation strategy assignment."""
    calc = Calculator()
    assert calc.operation_strategy is None

    op = Addition()
    calc.set_operation(op)
    assert calc.operation_strategy == op


def test_calculator_perform_operation_success():
    """Verify calculation execution and history update."""
    calc = Calculator()
    calc.set_operation(Addition())
    result = calc.perform_operation("10", "5")

    assert result == Decimal("15")
    assert len(calc.get_history()) == 1


def test_calculator_perform_operation_no_strategy_raises_error():
    """Verify OperationError when no operation is set."""
    calc = Calculator()
    with pytest.raises(OperationError, match="No operation set"):
        calc.perform_operation("1", "2")


def test_calculator_perform_operation_validation_error_reraised():
    """Verify ValidationError is re-raised directly."""
    calc = Calculator()
    calc.set_operation(Addition())
    with pytest.raises(ValidationError):
        calc.perform_operation("abc", "5")


def test_calculator_perform_operation_unexpected_exception_wrapped():
    """Verify unexpected errors during execution are wrapped in OperationError."""
    calc = Calculator()
    mock_op = MagicMock()
    mock_op.execute.side_effect = RuntimeError("Unexpected failure")
    calc.set_operation(mock_op)

    with pytest.raises(OperationError, match="Operation failed: Unexpected failure"):
        calc.perform_operation("10", "5")


def test_calculator_history_max_limit():
    """Verify history stack respects max_history_size configuration."""
    config = CalculatorConfig(max_history_size=2)
    calc = Calculator(config)
    calc.set_operation(Addition())

    calc.perform_operation("1", "1")
    calc.perform_operation("2", "2")
    calc.perform_operation("3", "3")

    history = calc.get_history()
    assert len(history) == 2
    assert history[0].operand1 == Decimal("2")
    assert history[1].operand1 == Decimal("3")


def test_calculator_observer_registration_and_notification():
    """Verify adding, removing, and notifying observers."""
    calc = Calculator()
    mock_observer = MagicMock()

    calc.add_observer(mock_observer)
    calc.add_observer(mock_observer)
    assert len(calc.observers) == 1

    calc.set_operation(Addition())
    calc.perform_operation("2", "3")
    mock_observer.update.assert_called_once()

    calc.remove_observer(mock_observer)
    assert len(calc.observers) == 0


def test_calculator_undo_redo_and_clear():
    """Verify Memento undo, redo, and clear_history behavior."""
    calc = Calculator()
    calc.set_operation(Addition())

    calc.perform_operation("1", "1")
    calc.perform_operation("2", "2")
    assert len(calc.get_history()) == 2

    assert calc.undo() is True
    assert len(calc.get_history()) == 1

    assert calc.redo() is True
    assert len(calc.get_history()) == 2

    calc.clear_history()
    assert len(calc.get_history()) == 0


def test_calculator_undo_redo_empty_raises_error():
    """Verify undo and redo on empty stack raise OperationError."""
    calc = Calculator()
    with pytest.raises(OperationError, match="No operations to undo"):
        calc.undo()

    with pytest.raises(OperationError, match="No operations to redo"):
        calc.redo()


def test_calculator_pandas_save_and_load_history(tmp_path):
    """Verify CSV history serialization and deserialization via pandas."""
    csv_file = tmp_path / "test_history.csv"
    calc = Calculator()
    calc.set_operation(Addition())
    calc.perform_operation("5", "10")

    calc.save_history(file_path=csv_file)
    assert csv_file.exists()

    new_calc = Calculator()
    new_calc.load_history(file_path=csv_file)
    assert len(new_calc.get_history()) == 1
    assert new_calc.get_history()[0].result == Decimal("15")


def test_calculator_save_history_failure_raises_operation_error(tmp_path):
    """Verify save_history raises OperationError on I/O error."""
    calc = Calculator()
    invalid_path = tmp_path / "non_existent_folder" / "sub" / "file.csv"
    with patch("pandas.DataFrame.to_csv", side_effect=PermissionError("Permission denied")):
        with pytest.raises(OperationError, match="Failed to save history"):
            calc.save_history(file_path=invalid_path)


def test_calculator_load_nonexistent_file_raises_error(tmp_path):
    """Verify load_history on missing file raises OperationError."""
    calc = Calculator()
    missing_file = tmp_path / "nonexistent.csv"
    with pytest.raises(OperationError, match="History file not found"):
        calc.load_history(file_path=missing_file)


def test_calculator_load_malformed_csv_raises_validation_error(tmp_path):
    """Verify load_history on malformed CSV raises ValidationError."""
    malformed_csv = tmp_path / "bad.csv"
    malformed_csv.write_text("invalid,header\n1,2")

    calc = Calculator()
    with pytest.raises(ValidationError, match="Malformed CSV file"):
        calc.load_history(file_path=malformed_csv)


def test_calculator_load_empty_csv_clears_history(tmp_path):
    """Verify loading empty CSV file clears current history."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("operation,operand1,operand2,result,timestamp\n")

    calc = Calculator()
    calc.set_operation(Addition())
    calc.perform_operation("1", "2")

    calc.load_history(file_path=empty_csv)
    assert len(calc.get_history()) == 0


def test_calculator_load_generic_exception_raises_operation_error(tmp_path):
    """Verify general exceptions during load_history raise OperationError."""
    bad_csv = tmp_path / "error.csv"
    bad_csv.write_text("operation,operand1,operand2,result,timestamp\nadd,1,2,3,2026-01-01")

    calc = Calculator()
    with patch("pandas.read_csv", side_effect=RuntimeError("Read failure")):
        with pytest.raises(OperationError, match="Failed to load history"):
            calc.load_history(file_path=bad_csv)

def test_calculator_remove_observer_when_present():
    """Verify removing an observer that is registered (True branch of 'if observer in self.observers:')."""
    calc = Calculator()
    mock_observer = MagicMock()

    calc.add_observer(mock_observer)
    assert mock_observer in calc.observers

    calc.remove_observer(mock_observer)
    assert mock_observer not in calc.observers

def test_calculator_remove_observer_when_not_present():
    """Verify removing an observer that was never added exits cleanly (False branch of 'if observer in self.observers:')."""
    calc = Calculator()
    mock_observer = MagicMock()

    assert mock_observer not in calc.observers

    # Calling remove_observer on an un-registered observer evaluates the condition to False and exits cleanly
    calc.remove_observer(mock_observer)
    assert len(calc.observers) == 0