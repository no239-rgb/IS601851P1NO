import datetime
from decimal import Decimal
import pytest
from unittest.mock import patch
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

@patch('app.calculation.OperationFactory.create_operation')
@pytest.mark.parametrize(
    "init_method, kwargs, expected_result",
    [
        (
            "from_dict",
            {
                "data": {
                    "operation": "add",
                    "operand1": "10",
                    "operand2": "5",
                    "result": "999",  # Intentionally incorrect math
                    "timestamp": datetime.datetime.now().isoformat()
                }
            },
            Decimal("999"),
        ),
        (
            "constructor_decimal",
            {
                "operation": "multiply",
                "operand1": Decimal("2"),
                "operand2": Decimal("3"),
                "result": Decimal("100"), 
            },
            Decimal("100"),
        ),
        (
            "constructor_string",
            {
                "operation": "subtract",
                "operand1": Decimal("10"),
                "operand2": Decimal("5"),
                "result": "500",  # String triggers the `elif not isinstance` branch
            },
            Decimal("500"),
        ),
        (
            "constructor_float",
            {
                "operation": "divide",
                "operand1": Decimal("20"),
                "operand2": Decimal("2"),
                "result": 50.5,  # Float triggers the `elif not isinstance` branch
            },
            Decimal("50.5"),
        ),
    ],
)
def test_calculation_avoids_recalculation_if_result_provided(
    mock_create_operation, init_method, kwargs, expected_result
):
    """Verify that providing a result during instantiation skips calculation and handles type conversion."""
    # Initialize using the specified method
    if init_method == "from_dict":
        calc = Calculation.from_dict(**kwargs)
    else:
        calc = Calculation(**kwargs)

    # Assert the loaded dead data is now alive, used, and correctly cast to a Decimal
    assert calc.result == expected_result
    assert isinstance(calc.result, Decimal)

    # Assert the factory was never called, proving double-execution is fixed
    mock_create_operation.assert_not_called()