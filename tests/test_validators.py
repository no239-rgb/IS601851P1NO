from decimal import Decimal
import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError
from app.input_validators import InputValidator


def test_input_validator_valid_numbers():
    """Verify string, int, and float inputs are converted to Decimal."""
    config = CalculatorConfig()

    assert InputValidator.validate_number(" 10 ", config) == Decimal("10")
    assert InputValidator.validate_number(25, config) == Decimal("25")
    assert InputValidator.validate_number(3.14, config) == Decimal("3.14")


def test_input_validator_exceeds_max_value_raises_validation_error():
    """Verify input exceeding max_input_value raises ValidationError."""
    config = CalculatorConfig(max_input_value=100)

    with pytest.raises(ValidationError, match="Value exceeds maximum allowed"):
        InputValidator.validate_number("105", config)


def test_input_validator_invalid_format_raises_validation_error():
    """Verify non-numeric strings raise ValidationError."""
    config = CalculatorConfig()

    with pytest.raises(ValidationError, match="Invalid number format: abc"):
        InputValidator.validate_number("abc", config)