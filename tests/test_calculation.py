import datetime
from decimal import Decimal
import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


@pytest.mark.parametrize(
    "operation, operand1, operand2, expected_result",
    [
        ("add", Decimal("5"), Decimal("3"), Decimal("8")),
        ("Addition", Decimal("10"), Decimal("20"), Decimal("30")),
        ("subtract", Decimal("10"), Decimal("4"), Decimal("6")),
        ("multiply", Decimal("3"), Decimal("4"), Decimal("12")),
        ("divide", Decimal("20"), Decimal("5"), Decimal("4")),
        ("power", Decimal("2"), Decimal("3"), Decimal("8")),
        ("root", Decimal("16"), Decimal("2"), Decimal("4")),
        ("modulus", Decimal("10"), Decimal("3"), Decimal("1")),
        ("Modulus", Decimal("10"), Decimal("3"), Decimal("1")),
        ("integer_division", Decimal("10"), Decimal("3"), Decimal("3")),
        ("IntegerDivision", Decimal("10"), Decimal("3"), Decimal("3")),
        ("absolute_difference", Decimal("5"), Decimal("12"), Decimal("7")),
        ("AbsoluteDifference", Decimal("12"), Decimal("5"), Decimal("7")),
        ("percentage", Decimal("25"), Decimal("100"), Decimal("25")),
        ("PercentageCalculation", Decimal("50"), Decimal("200"), Decimal("25")),
    ],
)
def test_calculation_creation_and_execution_success(operation, operand1, operand2, expected_result):
    """Test successful initialization and automatic calculation across all supported operations."""
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)
    assert calc.result == expected_result
    assert isinstance(calc.timestamp, datetime.datetime)


@pytest.mark.parametrize(
    "operation, operand1, operand2, error_match",
    [
        ("divide", Decimal("10"), Decimal("0"), "Division by zero is not allowed"),
        ("modulus", Decimal("10"), Decimal("0"), "Division by zero is not allowed"),
        ("integer_division", Decimal("10"), Decimal("0"), "Division by zero is not allowed"),
        ("percentage", Decimal("25"), Decimal("0"), "Division by zero is not allowed"),
        ("root", Decimal("-16"), Decimal("2"), "Cannot calculate root of negative number"),
        ("unknown_op", Decimal("5"), Decimal("5"), "Unknown operation: unknown_op"),
    ],
)
def test_calculation_execution_failure_raises_operation_error(operation, operand1, operand2, error_match):
    """Test that invalid mathematical operations or unknown factory keys raise OperationError."""
    with pytest.raises(OperationError, match=error_match):
        Calculation(operation=operation, operand1=operand1, operand2=operand2)


def test_calculation_to_dict():
    """Verify dictionary serialization format."""
    calc = Calculation(operation="modulus", operand1=Decimal("10"), operand2=Decimal("3"))
    data = calc.to_dict()

    assert data["operation"] == "modulus"
    assert data["operand1"] == "10"
    assert data["operand2"] == "3"
    assert data["result"] == "1"
    assert "timestamp" in data


def test_calculation_from_dict_success():
    """Verify Reconstruction of Calculation object from serialized dictionary data."""
    now_iso = datetime.datetime.now().isoformat()
    data = {
        "operation": "percentage",
        "operand1": "25",
        "operand2": "100",
        "result": "25",
        "timestamp": now_iso,
    }

    calc = Calculation.from_dict(data)
    assert calc.operation == "percentage"
    assert calc.operand1 == Decimal("25")
    assert calc.operand2 == Decimal("100")
    assert calc.result == Decimal("25")
    assert calc.timestamp.isoformat() == now_iso


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"operation": "add", "operand1": "10"},  # Missing operand2
        {"operation": "add", "operand1": "invalid_num", "operand2": "5"},  # Invalid Decimal string
        {"operation": "add", "operand1": "10", "operand2": "5", "timestamp": "invalid_date"},  # Invalid timestamp
    ],
)
def test_calculation_from_dict_failure(invalid_data):
    """Verify from_dict raises OperationError on malformed dictionary inputs."""
    with pytest.raises(OperationError, match="Invalid calculation data:"):
        Calculation.from_dict(invalid_data)


def test_calculation_string_representations():
    """Verify __str__ and __repr__ formatting."""
    calc = Calculation(operation="absolute_difference", operand1=Decimal("5"), operand2=Decimal("12"))

    assert str(calc) == "absolute_difference(5, 12) = 7"
    assert "Calculation(operation='absolute_difference'" in repr(calc)
    assert "result=7" in repr(calc)


def test_calculation_equality():
    """Verify equality comparison semantics."""
    calc1 = Calculation(operation="add", operand1=Decimal("5"), operand2=Decimal("5"))
    calc2 = Calculation(operation="add", operand1=Decimal("5"), operand2=Decimal("5"))
    calc3 = Calculation(operation="subtract", operand1=Decimal("5"), operand2=Decimal("5"))

    assert calc1 == calc2
    assert calc1 != calc3
    assert (calc1 == "not_a_calculation") is False


def test_calculation_format_result():
    """Verify result precision formatting."""
    calc = Calculation(operation="divide", operand1=Decimal("10"), operand2=Decimal("3"))
    formatted = calc.format_result(precision=4)
    assert formatted == "3.3333"