from decimal import Decimal
from unittest.mock import patch
import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.operations import Addition, OperationFactory


def test_calculator_initialization_default():
    """Test Calculator initialization with default configuration."""
    calc = Calculator()
    assert isinstance(calc.config, CalculatorConfig)
    assert calc.operation_strategy is None


def test_calculator_initialization_custom_config(tmp_path):
    """Test Calculator initialization with an explicit CalculatorConfig instance."""
    custom_config = CalculatorConfig(base_dir=tmp_path, precision=15)
    calc = Calculator(config=custom_config)
    assert calc.config == custom_config
    assert calc.config.precision == 15
    assert calc.operation_strategy is None


def test_set_operation():
    """Test assigning an operation strategy to the calculator."""
    calc = Calculator()
    op = OperationFactory.create_operation("add")
    calc.set_operation(op)
    assert calc.operation_strategy == op


@pytest.mark.parametrize(
    "op_name, operand_a, operand_b, expected_result",
    [
        ("add", 2, 3, Decimal("5")),
        ("subtract", "10", "4", Decimal("6")),
        ("multiply", Decimal("2.5"), Decimal("4"), Decimal("10")),
        ("divide", 20, "5", Decimal("4")),
        ("power", 2, 3, Decimal("8")),
        ("root", 16, 2, Decimal("4")),
    ],
)
def test_perform_operation_success(op_name, operand_a, operand_b, expected_result):
    """
    Test successful execution across various operations and input formats
    (int, str, Decimal).
    """
    calc = Calculator()
    op = OperationFactory.create_operation(op_name)
    calc.set_operation(op)

    result = calc.perform_operation(operand_a, operand_b)
    assert result == expected_result


def test_perform_operation_no_operation_set():
    """Test that attempting to calculate without setting an operation raises OperationError."""
    calc = Calculator()
    with pytest.raises(OperationError, match="No operation set"):
        calc.perform_operation(5, 5)


@pytest.mark.parametrize(
    "invalid_a, invalid_b, expected_error_msg",
    [
        ("not_a_number", 5, "Invalid number format"),
        (5, "abc", "Invalid number format"),
        ("1e1000", 2, "Value exceeds maximum allowed"),
    ],
)
def test_perform_operation_validation_errors(invalid_a, invalid_b, expected_error_msg):
    """Test that input validation failures raise ValidationError directly (not wrapped)."""
    calc = Calculator()
    calc.set_operation(OperationFactory.create_operation("add"))

    with pytest.raises(ValidationError, match=expected_error_msg):
        calc.perform_operation(invalid_a, invalid_b)


def test_perform_operation_generic_exception_wrapping():
    """Test that unexpected runtime execution exceptions are wrapped in an OperationError."""
    calc = Calculator()
    op = Addition()
    calc.set_operation(op)

    with patch.object(op, "execute", side_effect=RuntimeError("Execution failure")):
        with pytest.raises(OperationError, match="Operation failed: Execution failure"):
            calc.perform_operation(10, 5)