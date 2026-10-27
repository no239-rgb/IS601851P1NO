########################
# Calculation Model    #
########################

from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

from app.exceptions import OperationError, ValidationError
from app.operations import OperationFactory


@dataclass
class Calculation:
    """
    Value Object representing a single calculation.
    """

    operation: str          
    operand1: Decimal       
    operand2: Decimal       

    result: Decimal = field(init=False)  
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        """Automatically calculate the result after creation."""
        self.result = self.calculate()

    def calculate(self) -> Decimal:
        """Execute calculation by delegating to OperationFactory."""
        aliases = {
            "addition": "add",
            "subtraction": "subtract",
            "multiplication": "multiply",
            "division": "divide",
            "integerdivision": "integer_division",
            "int_divide": "integer_division",
            "absolutedifference": "absolute_difference",
            "abs_diff": "absolute_difference",
            "percentagecalculation": "percentage",
            "percent": "percentage",
        }
        op_key = self.operation.lower().replace(" ", "_")
        op_key = aliases.get(op_key, op_key)

        try:
            op_instance = OperationFactory.create_operation(op_key)
            return op_instance.execute(self.operand1, self.operand2)
        except (ValidationError, ValueError, InvalidOperation, ArithmeticError) as e:
            raise OperationError(f"Calculation failed: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert calculation to dictionary for serialization."""
        return {
            'operation': self.operation,
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        """Reconstruct a Calculation instance from a dictionary."""
        try:
            calc = Calculation(
                operation=data['operation'],
                operand1=Decimal(data['operand1']),
                operand2=Decimal(data['operand2'])
            )
            calc.timestamp = datetime.datetime.fromisoformat(data['timestamp'])            
            return calc
        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {str(e)}")

    def __str__(self) -> str:
        """Return string representation of calculation."""
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:
        """Return detailed string representation of calculation."""
        return (
            f"Calculation(operation='{self.operation}', "
            f"operand1={self.operand1}, "
            f"operand2={self.operand2}, "
            f"result={self.result}, "
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        """Check if two calculations are equal."""
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        """Format the result to a specified precision."""
        try:
            return str(self.result.normalize().quantize(
                Decimal('0.' + '0' * precision)
            ).normalize())
        except InvalidOperation:  # pragma: no cover
            return str(self.result)
