from decimal import Decimal
import pytest

from app.exceptions import ValidationError
from app.operations import (
    Addition,
    AbsoluteDifference,
    Division,
    IntegerDivision,
    Modulus,
    Multiplication,
    OperationFactory,
    PercentageCalculation,
    Power,
    Root,
    Subtraction,
)


def test_basic_operations():
    """Verify addition, subtraction, multiplication, and division."""
    assert Addition().execute(Decimal("2"), Decimal("3")) == Decimal("5")
    assert Subtraction().execute(Decimal("10"), Decimal("4")) == Decimal("6")
    assert Multiplication().execute(Decimal("3"), Decimal("4")) == Decimal("12")
    assert Division().execute(Decimal("10"), Decimal("2")) == Decimal("5")


def test_division_by_zero_raises_validation_error():
    """Verify division by zero raises ValidationError."""
    with pytest.raises(ValidationError, match="Division by zero is not allowed"):
        Division().execute(Decimal("10"), Decimal("0"))


def test_extended_operations():
    """Verify power, root, modulus, int_divide, abs_diff, and percentage."""
    assert Power().execute(Decimal("2"), Decimal("3")) == Decimal("8")
    assert Root().execute(Decimal("16"), Decimal("2")) == Decimal("4")
    assert Modulus().execute(Decimal("10"), Decimal("3")) == Decimal("1")
    assert IntegerDivision().execute(Decimal("10"), Decimal("3")) == Decimal("3")
    assert AbsoluteDifference().execute(Decimal("4"), Decimal("9")) == Decimal("5")
    assert PercentageCalculation().execute(Decimal("50"), Decimal("200")) == Decimal("25")


def test_power_edge_cases():
    """Verify power operation input constraints."""
    with pytest.raises(ValidationError, match="Cannot raise zero to a negative power"):
        Power().execute(Decimal("0"), Decimal("-2"))

    with pytest.raises(ValidationError, match="Negative base with non-integer exponent"):
        Power().execute(Decimal("-4"), Decimal("0.5"))


def test_root_edge_cases():
    """Verify root operation input constraints."""
    with pytest.raises(ValidationError, match="Cannot calculate root of negative number"):
        Root().execute(Decimal("-16"), Decimal("2"))

    with pytest.raises(ValidationError, match="Zero root is undefined"):
        Root().execute(Decimal("16"), Decimal("0"))


def test_factory_registration_and_creation():
    """Verify OperationFactory creation and subclass registration."""
    op = OperationFactory.create_operation("add")
    assert isinstance(op, Addition)

    with pytest.raises(ValueError, match="Unknown operation"):
        OperationFactory.create_operation("invalid")

    class CustomOp(Addition):
        pass

    OperationFactory.register_operation("custom", CustomOp)
    assert isinstance(OperationFactory.create_operation("custom"), CustomOp)

    with pytest.raises(TypeError, match="Operation class must inherit from Operation"):
        OperationFactory.register_operation("bad", object)

def test_factory_registration_and_creation():
    """Verify OperationFactory creation and subclass registration."""
    op = OperationFactory.create_operation("add")
    assert isinstance(op, Addition)

    with pytest.raises(ValueError, match="Unknown operation"):
        OperationFactory.create_operation("invalid")

    class CustomOp(Addition):
        pass

    OperationFactory.register_operation("custom", CustomOp)
    assert isinstance(OperationFactory.create_operation("custom"), CustomOp)

    with pytest.raises(TypeError, match="Operation class must inherit from Operation"):
        OperationFactory.register_operation("bad", object)

def test_factory_get_available_operations():
    """Verify that the factory correctly reports all registered operations."""
    ops = OperationFactory.get_available_operations()
    
    # Assert standard operations are present
    assert 'add' in ops
    assert 'subtract' in ops
    
    # Register a new operation and verify it appears dynamically
    class TestOp(Addition):
        pass
        
    OperationFactory.register_operation("dynamic_test", TestOp)
    updated_ops = OperationFactory.get_available_operations()
    
    assert "dynamic_test" in updated_ops

def test_root_preserves_decimal_precision():
    """Verify Root calculation stays within the Decimal type and maintains precision."""
    a = Decimal("100")
    b = Decimal("2")
    
    result = Root().execute(a, b)

    assert isinstance(result, Decimal)
    assert result == Decimal("10")