import os
from decimal import Decimal
from pathlib import Path
import pytest

from app.calculator_config import CalculatorConfig, get_project_root
from app.exceptions import ConfigurationError


def test_get_project_root():
    """Verify get_project_root locates parent directory of app module."""
    root = get_project_root()
    assert root.exists()
    assert (root / "app").exists()


def test_calculator_config_defaults(monkeypatch, tmp_path):
    """Verify default values when environment variables are unset."""
    monkeypatch.setattr("app.calculator_config.get_project_root", lambda: tmp_path)
    monkeypatch.delenv("CALCULATOR_BASE_DIR", raising=False)
    monkeypatch.delenv("CALCULATOR_PRECISION", raising=False)
    monkeypatch.delenv("CALCULATOR_MAX_INPUT_VALUE", raising=False)
    monkeypatch.delenv("CALCULATOR_DEFAULT_ENCODING", raising=False)
    monkeypatch.delenv("CALCULATOR_LOG_DIR", raising=False)
    monkeypatch.delenv("CALCULATOR_HISTORY_DIR", raising=False)
    monkeypatch.delenv("CALCULATOR_HISTORY_FILE", raising=False)
    monkeypatch.delenv("CALCULATOR_LOG_FILE", raising=False)
    monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    monkeypatch.delenv("CALCULATOR_AUTO_SAVE", raising=False)

    config = CalculatorConfig()
    config.validate()

    assert config.precision == 10
    assert config.max_input_value == Decimal("1e999")
    assert config.default_encoding == "utf-8"
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.history_file == (tmp_path / "history" / "history.csv").resolve()
    assert config.log_file == (tmp_path / "logs" / "app.log").resolve()


def test_calculator_config_custom_values():
    """Verify explicit constructor overrides take precedence."""
    base = Path("/tmp/calc")
    config = CalculatorConfig(
        base_dir=base,
        precision=5,
        max_input_value=1000,
        default_encoding="ascii",
        max_history_size=50,
        auto_save=False,
    )

    assert config.precision == 5
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == "ascii"
    assert config.max_history_size == 50
    assert config.auto_save is False


@pytest.mark.parametrize(
    "invalid_kwargs, error_msg",
    [
        ({"precision": 0}, "precision must be positive"),
        ({"max_input_value": -10}, "max_input_value must be positive"),
        ({"max_history_size": 0}, "max_history_size must be positive"),
    ],
)
def test_calculator_config_validation_failures(invalid_kwargs, error_msg):
    """Verify validation exceptions for non-positive bounds."""
    config = CalculatorConfig(**invalid_kwargs)
    with pytest.raises(ConfigurationError, match=error_msg):
        config.validate()
