#############################################
#           Calculator Configuration        #
#############################################

from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

# Load environment variables from a .env file into the program's environment
load_dotenv()


def get_project_root() -> Path:
    """
    Get the project root directory.

    This function determines the root directory of the project by navigating up
    the directory hierarchy from the current file's location.

    Returns:
        Path: The root directory path of the project.
    """
    # Get the directory of the current file (app/calculator_config.py)
    current_file = Path(__file__)
    # Navigate up two levels to reach the project root (from app/calculator_config.py to project root)
    return current_file.parent.parent


@dataclass
class CalculatorConfig:
    """
    Calculator configuration settings.

    This class manages all configuration parameters required by the calculator
    application, including directory paths, calculation precision, maximum input values, 
    and default encoding.

    Configuration can be set via environment variables or by passing parameters
    directly to the class constructor.
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,       
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None
    ):
        """
        Initialize configuration with environment variables and defaults.

        Args:
            base_dir (Optional[Path], optional): Base directory for the calculator. Defaults to None.
            precision (Optional[int], optional): Number of decimal places for calculations. Defaults to None.
            max_input_value (Optional[Number], optional): Maximum allowed input value. Defaults to None.
            default_encoding (Optional[str], optional): Default encoding for file operations. Defaults to None.
        """
        # Set base directory to project root by default
        project_root = get_project_root()
        self.base_dir = base_dir or Path(
            os.getenv('CALCULATOR_BASE_DIR', str(project_root))
        ).resolve()

        # Calculation precision
        self.precision = (
            precision if precision is not None 
            else int(os.getenv('CALCULATOR_PRECISION', '10'))
        )

        # Maximum input value allowed
        self.max_input_value = (
            max_input_value if max_input_value is not None 
            else Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e999'))
        )

        # Default encoding for file operations
        self.default_encoding = default_encoding or os.getenv(
            'CALCULATOR_DEFAULT_ENCODING', 'utf-8'
        )

    def validate(self) -> None:
        """
        Validate configuration settings.

        Ensures that all configuration parameters meet the required criteria.
        Raises ConfigurationError if any validation fails.

        Raises:
            ConfigurationError: If any configuration parameter is invalid.
        """
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")