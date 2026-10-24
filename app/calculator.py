########################
# Calculator Class     #
########################

from decimal import Decimal
from pathlib import Path
from typing import Optional, Union
from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.input_validators import InputValidator
from app.operations import Operation

# Type aliases for better readability
Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]


class Calculator:
    """
    Main calculator class implementing multiple design patterns.

    This class serves as the core of the calculator application, managing operations,
    and configuration settings. 
    It integrates various design patterns to enhance flexibility, maintainability, and
    scalability.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        """
        Initialize calculator with configuration.

        Args:
            config (Optional[CalculatorConfig], optional): Configuration settings for the calculator.
                If not provided, default settings are loaded based on environment variables.
        """
        if config is None:
            # Determine the project root directory if no configuration is provided
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        # Assign the configuration and validate its parameters
        self.config = config
        self.config.validate()

        # Initialize operation strategy
        self.operation_strategy: Optional[Operation] = None

    def set_operation(self, operation: Operation) -> None:
        """
        Set the current operation strategy.

        Assigns the operation strategy that will be used for performing calculations.
        This is part of the Strategy pattern, allowing the calculator to switch between
        different operation algorithms dynamically.

        Args:
            operation (Operation): The operation strategy to be set.
        """
        self.operation_strategy = operation
      

    def perform_operation(
        self,
        a: Union[str, Number],
        b: Union[str, Number]
    ) -> CalculationResult:
        """
        Perform calculation with the current operation.

        Validates and sanitizes user inputs, executes the calculation using the
        current operation strategy, updates the history, and notifies observers.

        Args:
            a (Union[str, Number]): The first operand, can be a string or a numeric type.
            b (Union[str, Number]): The second operand, can be a string or a numeric type.

        Returns:
            CalculationResult: The result of the calculation.

        Raises:
            OperationError: If no operation is set or if the operation fails.
            ValidationError: If input validation fails.
        """
        if not self.operation_strategy:
            raise OperationError("No operation set")

        try:
            # Validate and convert inputs to Decimal
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            # Execute the operation strategy
            result = self.operation_strategy.execute(validated_a, validated_b)

            return result

        except ValidationError as e:
            # Re-raise ValidationError directly so it isn't wrapped as an OperationError        
            raise
        except Exception as e:
            # Catch any other unexpected exception and wrap it as an OperationError         
            raise OperationError(f"Operation failed: {str(e)}")


        

