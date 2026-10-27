from decimal import Decimal
import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError
from app.input_validators import InputValidator


@pytest.fixture
def config():
    """Test configuration with a fixed max_input_value boundary."""
    return CalculatorConfig(max_input_value=Decimal("1000000"))


@pytest.mark.parametrize(
    "input_value, expected_decimal",
    [
        (123, Decimal("123")),
        (123.456, Decimal("123.456").normalize()),
        ("123", Decimal("123")),
        ("123.456", Decimal("123.456").normalize()),
        (-789, Decimal("-789")),
        (-789.123, Decimal("-789.123").normalize()),
        ("-789", Decimal("-789")),
        ("-789.123", Decimal("-789.123").normalize()),
        (0, Decimal("0")),
        ("0", Decimal("0")),
        ("  456  ", Decimal("456")),
    ],
)
def test_validate_number_success(config, input_value, expected_decimal):
    """Verify valid numeric inputs (integers, floats, strings, negative values, and padded whitespace) convert correctly."""
    result = InputValidator.validate_number(input_value, config)
    assert result == expected_decimal


@pytest.mark.parametrize(
    "input_value, expected_error_msg",
    [
        ("abc", "Invalid number format: abc"),
        ("", "Invalid number format: "),
        ("   ", "Invalid number format: "),
        (None, "Invalid number format: None"),
        ([], "Invalid number format: "),
        (Decimal("1000001"), "Value exceeds maximum allowed"),
        ("1000001", "Value exceeds maximum allowed"),
        (Decimal("-1000001"), "Value exceeds maximum allowed"),
        ("-1000001", "Value exceeds maximum allowed"),
    ],
)
def test_validate_number_exceptions(config, input_value, expected_error_msg):
    """Verify invalid numeric formats, non-numeric types, and values exceeding max_input_value raise ValidationError."""
    with pytest.raises(ValidationError, match=expected_error_msg):
        InputValidator.validate_number(input_value, config)