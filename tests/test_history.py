import logging
from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from app.calculation import Calculation
from app.history import AutoSaveObserver, HistoryObserver, LoggingObserver


def test_history_observer_abstract_instantiation():
    """Verify HistoryObserver abstract base class cannot be instantiated."""
    with pytest.raises(TypeError):
        HistoryObserver()


def test_logging_observer_update_success(caplog):
    """Verify LoggingObserver delegates calculation log events to Logger."""
    observer = LoggingObserver()
    calc = Calculation(operation="add", operand1=Decimal("10"), operand2=Decimal("5"))

    with caplog.at_level(logging.INFO):
        observer.update(calc)

    assert "Calculation performed: add (10, 5) = 15" in caplog.text


def test_logging_observer_update_none_raises_attribute_error():
    """Verify LoggingObserver raises AttributeError on None."""
    observer = LoggingObserver()
    with pytest.raises(AttributeError, match="Calculation cannot be None"):
        observer.update(None)


def test_autosave_observer_init_validation():
    """Verify AutoSaveObserver constructor checks for required calculator attributes."""
    valid_calc = MagicMock(config=MagicMock(), save_history=MagicMock())
    observer = AutoSaveObserver(valid_calc)
    assert observer.calculator == valid_calc

    invalid_calc = object()
    with pytest.raises(TypeError, match="Calculator must have 'config' and 'save_history' attributes"):
        AutoSaveObserver(invalid_calc)


def test_autosave_observer_update_auto_save_enabled(caplog):
    """Verify AutoSaveObserver triggers save_history when config auto_save is True."""
    mock_calc = MagicMock()
    mock_calc.config.auto_save = True
    observer = AutoSaveObserver(mock_calc)
    calc = Calculation(operation="add", operand1=Decimal("2"), operand2=Decimal("3"))

    with caplog.at_level(logging.INFO):
        observer.update(calc)

    mock_calc.save_history.assert_called_once()
    assert "History auto-saved" in caplog.text


def test_autosave_observer_update_auto_save_disabled(caplog):
    """Verify AutoSaveObserver skips save_history when config auto_save is False."""
    mock_calc = MagicMock()
    mock_calc.config.auto_save = False
    observer = AutoSaveObserver(mock_calc)
    calc = Calculation(operation="add", operand1=Decimal("2"), operand2=Decimal("3"))

    with caplog.at_level(logging.INFO):
        observer.update(calc)

    mock_calc.save_history.assert_not_called()
    assert "History auto-saved" not in caplog.text


def test_autosave_observer_update_none_raises_attribute_error():
    """Verify AutoSaveObserver raises AttributeError on None."""
    mock_calc = MagicMock()
    mock_calc.config.auto_save = True
    observer = AutoSaveObserver(mock_calc)

    with pytest.raises(AttributeError, match="Calculation cannot be None"):
        observer.update(None)