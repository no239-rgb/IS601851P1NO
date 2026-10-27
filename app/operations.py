###################################################
#     Operations Classes                          #
###################################################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError

class Operation(ABC):
    """
    Abstract base class for calculator operations.
    """

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Executes the operation.
        """

        pass # pragma: no cover
   

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands before execution.
        """

        pass

    def __str__(self) -> str:
        """
        Return operation name for display.
        """

        return self.__class__.__name__

class NonZeroDivisorMixin:
    """
    Mixin to add zero-divisor validation to any Operation class.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands, checking for division by zero.
        """

        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

class Addition(Operation):
    """
    Addition operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b
    
class Subtraction(Operation):
    """
    Subtraction operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b

class Multiplication(Operation):
    """
    Multiplication operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b

class Division(NonZeroDivisorMixin, Operation):
    """
    Division operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b

class Power(Operation):
    """
    Power operation implementation.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a == 0 and b < 0:
            raise ValidationError("Cannot raise zero to a negative power")
        if a < 0 and b % 1 != 0:
            raise ValidationError("Negative base with non-integer exponent is not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a ** b

class Root(Operation):
    """
    Root operation implementation.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))

class Modulus(NonZeroDivisorMixin, Operation):
    """
    Modulus operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a % b

class IntegerDivision(NonZeroDivisorMixin, Operation):
    """
    Integer division operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a // b

class AbsoluteDifference(Operation):
    """
    Absolute difference operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return abs(a - b)

class PercentageCalculation(NonZeroDivisorMixin, Operation):
    """
    Percentage calculation operation implementation.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return (a / b) * 100

class OperationFactory:
    """
    Factory class for creating operation instances.
    """

    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
        'modulus': Modulus,
        'integer_division': IntegerDivision,
        'int_divide': IntegerDivision,
        'absolute_difference': AbsoluteDifference,
        'abs_diff': AbsoluteDifference,
        'percentage': PercentageCalculation,
        'percent': PercentageCalculation,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """
        Register a new operation type.
        """

        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create an operation instance based on type.
        """

        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()   
    
