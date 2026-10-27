import pytest
from datetime import datetime
from decimal import Decimal

from app.calculation import Calculation
from app.exceptions import OperationError


@pytest.mark.parametrize(
    "operation, operand1, operand2, expected",
    [
        ("Addition", Decimal("2"), Decimal("3"), Decimal("5")),
        ("add", Decimal("10"), Decimal("5"), Decimal("15")),
        ("Subtraction", Decimal("5"), Decimal("3"), Decimal("2")),
        ("subtract", Decimal("10"), Decimal("4"), Decimal("6")),
        ("Multiplication", Decimal("4"), Decimal("2"), Decimal("8")),
        ("multiply", Decimal("3"), Decimal("3"), Decimal("9")),
        ("Division", Decimal("8"), Decimal("2"), Decimal("4")),
        ("divide", Decimal("20"), Decimal("5"), Decimal("4")),
        ("Power", Decimal("2"), Decimal("3"), Decimal("8")),
        ("power", Decimal("5"), Decimal("2"), Decimal("25")),
        ("Root", Decimal("16"), Decimal("2"), Decimal("4")),
        ("root", Decimal("27"), Decimal("3"), Decimal("3")),
    ]
)
def test_successful_calculations(operation, operand1, operand2, expected):
    """
    Test valid calculation execution using parametrized inputs across standard
    operation names and lower-case factory keys.
    """
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)
    assert calc.result == expected


@pytest.mark.parametrize(
    "operation, operand1, operand2, expected_error_msg",
    [
        (
            "Division",
            Decimal("8"),
            Decimal("0"),
            "Calculation failed: Division by zero is not allowed"
        ),
        (
            "Power",
            Decimal("0"),
            Decimal("-1"),
            "Calculation failed: Cannot raise zero to a negative power"
        ),
        (
            "Power",
            Decimal("-4"),
            Decimal("0.5"),
            "Calculation failed: Negative base with non-integer exponent is not supported"
        ),
        (
            "Root",
            Decimal("-16"),
            Decimal("2"),
            "Calculation failed: Cannot calculate root of negative number"
        ),
        (
            "Root",
            Decimal("16"),
            Decimal("0"),
            "Calculation failed: Zero root is undefined"
        ),
        (
            "Unknown",
            Decimal("5"),
            Decimal("3"),
            "Calculation failed: Unknown operation: unknown"
        ),
        (
            "Subtraction",
            Decimal("Infinity"),
            Decimal("Infinity"),
            "Calculation failed:"
        ),
    ]
)
def test_calculation_failures(operation, operand1, operand2, expected_error_msg):
    """
    Test calculation failures to verify that OperationError is raised with the
    'Calculation failed:' prefix as formatted by the updated calculate() method.
    """
    with pytest.raises(OperationError, match=expected_error_msg):
        Calculation(operation=operation, operand1=operand1, operand2=operand2)


def test_to_dict():
    """Test serialization of Calculation instance to dictionary format."""
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }


def test_from_dict():
    """Test deserialization of a dictionary into a Calculation instance."""
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == "Addition"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")


def test_invalid_from_dict():
    """Test that invalid dictionary payload triggers an OperationError."""
    data = {
        "operation": "Addition",
        "operand1": "invalid_number",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


def test_format_result():
    """Test formatting calculation results to specific precision levels."""
    calc = Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"


def test_string_representation():
    """Test __str__ output formatting."""
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert str(calc) == "Addition(2, 3) = 5"


def test_repr_representation():
    """Test __repr__ detailed string representation."""
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    expected_repr = (
        f"Calculation(operation='Addition', "
        f"operand1=2, "
        f"operand2=3, "
        f"result=5, "
        f"timestamp='{calc.timestamp.isoformat()}')"
    )
    assert repr(calc) == expected_repr


def test_equality():
    """Test equality (__eq__) comparison across identical and non-identical objects."""
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))

    assert calc1 == calc2
    assert calc1 != calc3
    assert calc1 != "string_object"
    assert calc1 != 42
    assert calc1 is not None