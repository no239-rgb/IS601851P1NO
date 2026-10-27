import pytest
from app.exceptions import (
    CalculatorError,  # Note: Change to CalculationError if matching exceptions.py exactly
    ValidationError,
    OperationError,
    ConfigurationError,
)

@pytest.mark.parametrize(
    "exception_cls, message",
    [
        (CalculatorError, "Base calculator error occurred"),
        (ValidationError, "Validation failed"),
        (OperationError, "Operation failed"),
        (ConfigurationError, "Configuration invalid"),
    ],
)
def test_exceptions_inherit_from_base_calculator_error(exception_cls, message):
    """Verify that all custom exception subclasses are caught by the base CalculatorError handler."""
    with pytest.raises(CalculatorError) as exc_info:
        raise exception_cls(message)
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == message


@pytest.mark.parametrize(
    "exception_cls, message",
    [
        (CalculatorError, "Base calculator error occurred"),
        (ValidationError, "Specific validation error"),
        (OperationError, "Specific operation error"),
        (ConfigurationError, "Specific configuration error"),
    ],
)
def test_exceptions_caught_by_specific_class(exception_cls, message):
    """Verify that each exception type can be caught specifically by its own class type."""
    with pytest.raises(exception_cls) as exc_info:
        raise exception_cls(message)
    assert str(exc_info.value) == message