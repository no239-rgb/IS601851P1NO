from decimal import Decimal
import pytest

from app.exceptions import ValidationError
from app.operations import (
    Addition,
    Division,
    Multiplication,
    Operation,
    OperationFactory,
    Power,
    Root,
    Subtraction,
)


@pytest.mark.parametrize(
    "op_class, a, b, expected",
    [
        (Addition, Decimal("5"), Decimal("3"), Decimal("8")),
        (Subtraction, Decimal("10"), Decimal("4"), Decimal("6")),
        (Multiplication, Decimal("3"), Decimal("4"), Decimal("12")),
        (Division, Decimal("20"), Decimal("5"), Decimal("4")),
        (Power, Decimal("2"), Decimal("3"), Decimal("8")),
        (Power, Decimal("2"), Decimal("-2"), Decimal("0.25")),
        (Power, Decimal("-2"), Decimal("3"), Decimal("-8")),
        (Root, Decimal("16"), Decimal("2"), Decimal("4")),
        (Root, Decimal("27"), Decimal("3"), Decimal("3")),
    ],
)
def test_operations_execute_success(op_class, a, b, expected):
    """Test successful execution of all arithmetic operations."""
    op = op_class()
    result = op.execute(a, b)
    assert result == expected


@pytest.mark.parametrize(
    "op_class, a, b, expected_error_msg",
    [
        (Division, Decimal("5"), Decimal("0"), "Division by zero is not allowed"),
        (Power, Decimal("0"), Decimal("-1"), "Cannot raise zero to a negative power"),
        (Power, Decimal("-4"), Decimal("0.5"), "Negative base with non-integer exponent is not supported"),
        (Root, Decimal("-16"), Decimal("2"), "Cannot calculate root of negative number"),
        (Root, Decimal("16"), Decimal("0"), "Zero root is undefined"),
    ],
)
def test_operations_validation_errors(op_class, a, b, expected_error_msg):
    """Test validation constraints across Division, Power, and Root operations."""
    op = op_class()
    with pytest.raises(ValidationError, match=expected_error_msg):
        op.execute(a, b)


@pytest.mark.parametrize(
    "op_class, expected_name",
    [
        (Addition, "Addition"),
        (Subtraction, "Subtraction"),
        (Multiplication, "Multiplication"),
        (Division, "Division"),
        (Power, "Power"),
        (Root, "Root"),
    ],
)
def test_operation_str(op_class, expected_name):
    """Test __str__ method returns the exact class name for display."""
    op = op_class()
    assert str(op) == expected_name


@pytest.mark.parametrize(
    "key, expected_class",
    [
        ("add", Addition),
        ("ADD", Addition),
        ("subtract", Subtraction),
        ("multiply", Multiplication),
        ("divide", Division),
        ("power", Power),
        ("root", Root),
    ],
)
def test_factory_create_operation_success(key, expected_class):
    """Test factory creates correct operation instances case-insensitively."""
    op = OperationFactory.create_operation(key)
    assert isinstance(op, expected_class)


def test_factory_create_unknown_operation():
    """Test factory raises ValueError when requested operation is not registered."""
    with pytest.raises(ValueError, match="Unknown operation: modulo"):
        OperationFactory.create_operation("modulo")


def test_factory_register_custom_operation():
    """Test dynamically registering a valid custom operation class in OperationFactory."""

    class Modulus(Operation):
        def execute(self, a: Decimal, b: Decimal) -> Decimal:
            self.validate_operands(a, b)
            return a % b

    OperationFactory.register_operation("modulus", Modulus)
    op = OperationFactory.create_operation("modulus")

    assert isinstance(op, Modulus)
    assert op.execute(Decimal("10"), Decimal("3")) == Decimal("1")


def test_factory_register_invalid_operation():
    """Test registering a class that does not inherit from Operation raises TypeError."""

    class InvalidOp:
        pass

    with pytest.raises(TypeError, match="Operation class must inherit from Operation"):
        OperationFactory.register_operation("invalid", InvalidOp)