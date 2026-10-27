import logging
from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from app.calculation import Calculation
from app.logger import Logger


def test_logger_configure_with_config(tmp_path):
    """Verify Logger creates log directory and configures logging."""
    mock_config = MagicMock()
    mock_config.log_dir = tmp_path / "logs"
    mock_config.log_file_name = "test.log"

    Logger.configure(mock_config)

    assert (tmp_path / "logs").exists()
    assert Logger._configured is True


def test_logger_configure_fallback_default(tmp_path, monkeypatch):
    """Verify Logger falls back to local logs dir when config is None."""
    monkeypatch.chdir(tmp_path)
    Logger.configure(None)

    assert (tmp_path / "logs").exists()


def test_logger_info_warning_error(caplog):
    """Verify Logger static logging methods record at expected levels."""
    with caplog.at_level(logging.INFO):
        Logger.info("Info test")
        Logger.warning("Warn test")
        Logger.error("Error test")

    assert "Info test" in caplog.text
    assert "Warn test" in caplog.text
    assert "Error test" in caplog.text


def test_logger_log_calculation_success(caplog):
    """Verify log_calculation formats calculation object output."""
    calc = Calculation(operation="add", operand1=Decimal("10"), operand2=Decimal("5"))

    with caplog.at_level(logging.INFO):
        Logger.log_calculation(calc)

    assert "Calculation performed: add (10, 5) = 15" in caplog.text


def test_logger_log_calculation_none_raises_attribute_error():
    """Verify log_calculation raises AttributeError when calculation is None."""
    with pytest.raises(AttributeError, match="Calculation cannot be None"):
        Logger.log_calculation(None)