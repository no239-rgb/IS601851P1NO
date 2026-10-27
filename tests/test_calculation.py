import datetime
from decimal import Decimal
import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


def test_calculation_creation_and_calculate():
    """Verify calculation post_init computes the result."""
    calc = Calculation(operation="add", operand1=Decimal("10"), operand2=Decimal("5"))
    assert calc.result == Decimal("15")


@pytest.mark.parametrize(
    "op_alias, a, b, expected",
    [
        ("addition", Decimal("2"), Decimal("3"), Decimal("5")),
        ("int_divide", Decimal("10"), Decimal("3"), Decimal("3")),
        ("abs_diff", Decimal("4"), Decimal("9"), Decimal("5")),
        ("percent", Decimal("50"), Decimal("200"), Decimal("25")),
    ],
)
def test_calculation_operation_aliases(op_alias, a, b, expected):
    """Verify calculation resolves operational string aliases."""
    calc = Calculation(operation=op_alias, operand1=a, operand2=b)
    assert calc.result == expected


def test_calculation_invalid_op_raises_operation_error():
    """Verify invalid operation name raises OperationError."""
    with pytest.raises(OperationError, match="Calculation failed"):
        Calculation(operation="unknown_op", operand1=Decimal("1"), operand2=Decimal("2"))


def test_calculation_from_dict_malformed_raises_operation_error():
    """Verify from_dict raises OperationError on invalid or missing keys."""
    invalid_dict = {"operation": "add", "operand1": "invalid_number", "operand2": "5"}
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(invalid_dict)


def test_calculation_serialization():
    """Verify calculation to_dict, from_dict, __str__, and __repr__."""
    calc = Calculation(operation="subtract", operand1=Decimal("10"), operand2=Decimal("4"))
    d = calc.to_dict()

    assert d["operation"] == "subtract"
    assert d["result"] == "6"

    restored = Calculation.from_dict(d)
    assert restored == calc

    assert str(calc) == "subtract(10, 4) = 6"
    assert "Calculation(operation='subtract'" in repr(calc)


def test_calculation_equality_and_format():
    """Verify equality comparison and result formatting."""
    c1 = Calculation(operation="add", operand1=Decimal("1"), operand2=Decimal("2"))
    c2 = Calculation(operation="add", operand1=Decimal("1"), operand2=Decimal("2"))
    assert c1 == c2
    assert c1 != "not_a_calculation"

    assert c1.format_result(precision=2) == "3"