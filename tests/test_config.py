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
        # Numeric Bounds
        ({"precision": 0}, "precision must be positive"),
        ({"precision": -5}, "precision must be positive"),
        ({"max_input_value": 0}, "max_input_value must be positive"),
        ({"max_input_value": -10}, "max_input_value must be positive"),
        ({"max_history_size": 0}, "max_history_size must be positive"),
        ({"max_history_size": -1}, "max_history_size must be positive"),

        # Encoding Checks
        ({"default_encoding": ""}, "default_encoding must be a non-empty string"),
        ({"default_encoding": 123}, "default_encoding must be a non-empty string"),
        ({"default_encoding": "invalid-codec-123"}, "invalid default_encoding"),

        # File Names
        ({"history_file_name": ""}, "history_file_name must be a non-empty string"),
        ({"history_file_name": 123}, "history_file_name must be a non-empty string"),
        ({"log_file_name": ""}, "log_file_name must be a non-empty string"),
        ({"log_file_name": 123}, "log_file_name must be a non-empty string"),

        # Paths & Type Integrity
        ({"base_dir": "not_a_path_object"}, "base_dir must be a valid Path object"),
        ({"auto_save": "not_a_bool"}, "auto_save must be a boolean value"),
    ],
)
def test_calculator_config_validation_failures(invalid_kwargs, error_msg):
    """Verify initialization raises ConfigurationError for invalid settings immediately on creation."""
    with pytest.raises(ConfigurationError, match=error_msg):
        CalculatorConfig(**invalid_kwargs)

@pytest.mark.parametrize(
    "env_var, invalid_value, expected_error_match",
    [
        ("CALCULATOR_PRECISION", "abc", "CALCULATOR_PRECISION must be a valid integer"),
        ("CALCULATOR_MAX_INPUT_VALUE", "not_a_number", "CALCULATOR_MAX_INPUT_VALUE must be a valid number"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "xyz", "CALCULATOR_MAX_HISTORY_SIZE must be a valid integer"),
    ],
)
def test_calculator_config_invalid_env_types_raise_configuration_error(
    monkeypatch, env_var, invalid_value, expected_error_match
):
    """Verify that invalid environment variable types are sanitized into ConfigurationError."""
    # Mock the specific environment variable with an invalid string
    monkeypatch.setenv(env_var, invalid_value)

    with pytest.raises(ConfigurationError, match=expected_error_match):
        CalculatorConfig()

def test_calculator_config_invalid_boolean_env_fallback(monkeypatch):
    """Verify that invalid boolean strings gracefully fallback or raise ConfigurationError."""
    # Depending on implementation, you might want this to raise an error or default to False.
    # If standardizing strict boundary validation:
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "not_a_bool_string")
    
    # If the fix enforces strict boolean parsing:
    with pytest.raises(ConfigurationError, match="CALCULATOR_AUTO_SAVE must be a boolean"):
        CalculatorConfig()

@pytest.mark.parametrize("false_val", ["false", "0", "no", "f"])
def test_calculator_config_auto_save_env_false_branch(monkeypatch, false_val):
    """Verify that env CALCULATOR_AUTO_SAVE set to a false string evaluates self.auto_save to False."""
    # Set the environment variable to a false string variant
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", false_val)

    # Instantiate without passing auto_save explicitly so it executes the 'else' branch
    config = CalculatorConfig(auto_save=None)

    # Assert that self.auto_save reached the target line and set self.auto_save to False
    assert config.auto_save is False