import os
from decimal import Decimal
from pathlib import Path
import pytest
from unittest.mock import patch

from app.calculator_config import CalculatorConfig, get_project_root
from app.exceptions import ConfigurationError


def test_get_project_root():
    """Test that get_project_root returns a valid Path object pointing to the project root."""
    root = get_project_root()
    assert isinstance(root, Path)
    assert root.exists()


def test_default_config_initialization():
    """Test default initialization values when no arguments or env vars are supplied."""
    with patch.dict(os.environ, {}, clear=True):
        config = CalculatorConfig()
        assert config.base_dir == get_project_root().resolve()
        assert config.precision == 10
        assert config.max_input_value == Decimal("1e999")
        assert config.default_encoding == "utf-8"


@pytest.mark.parametrize(
    "precision, max_input_value, default_encoding, expected_precision, expected_max_input, expected_encoding",
    [
        (5, Decimal("1000"), "ascii", 5, Decimal("1000"), "ascii"),
        (15, Decimal("1e50"), "utf-16", 15, Decimal("1e50"), "utf-16"),
        (20, 500, "utf-8", 20, Decimal("500"), "utf-8"),
    ]
)
def test_custom_config_initialization(
    precision,
    max_input_value,
    default_encoding,
    expected_precision,
    expected_max_input,
    expected_encoding,
    tmp_path
):
    """Test instantiating CalculatorConfig with explicit custom parameters."""
    config = CalculatorConfig(
        base_dir=tmp_path,
        precision=precision,
        max_input_value=max_input_value,
        default_encoding=default_encoding
    )
    assert config.base_dir == tmp_path
    assert config.precision == expected_precision
    assert config.max_input_value == expected_max_input
    assert config.default_encoding == expected_encoding


@pytest.mark.parametrize(
    "env_vars, expected_precision, expected_max_input, expected_encoding",
    [
        (
            {
                "CALCULATOR_PRECISION": "8",
                "CALCULATOR_MAX_INPUT_VALUE": "5000",
                "CALCULATOR_DEFAULT_ENCODING": "latin-1",
            },
            8,
            Decimal("5000"),
            "latin-1",
        ),
        (
            {
                "CALCULATOR_PRECISION": "12",
                "CALCULATOR_MAX_INPUT_VALUE": "1e100",
                "CALCULATOR_DEFAULT_ENCODING": "utf-8",
            },
            12,
            Decimal("1e100"),
            "utf-8",
        ),
    ]
)
def test_config_from_environment(env_vars, expected_precision, expected_max_input, expected_encoding):
    """Test loading configuration parameters from environment variables."""
    with patch.dict(os.environ, env_vars, clear=True):
        config = CalculatorConfig()
        assert config.precision == expected_precision
        assert config.max_input_value == expected_max_input
        assert config.default_encoding == expected_encoding


def test_valid_configuration_validation():
    """Test that validate() succeeds without raising an exception for valid parameters."""
    config = CalculatorConfig(precision=10, max_input_value=Decimal("1e10"))
    config.validate()  # Passes if no exception is raised


@pytest.mark.parametrize(
    "precision, max_input_value, expected_error_msg",
    [
        (0, Decimal("100"), "precision must be positive"),
        (-5, Decimal("100"), "precision must be positive"),
        (10, Decimal("0"), "max_input_value must be positive"),
        (10, Decimal("-50"), "max_input_value must be positive"),
    ]
)
def test_invalid_config_validation(precision, max_input_value, expected_error_msg):
    """Test that validate() raises ConfigurationError when given non-positive parameters."""
    config = CalculatorConfig(precision=precision, max_input_value=max_input_value)
    with pytest.raises(ConfigurationError, match=expected_error_msg):
        config.validate()