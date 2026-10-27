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

    Returns:
        Path: The root directory path of the project.
    """
    current_file = Path(__file__)
    return current_file.parent.parent


@dataclass
class CalculatorConfig:
    """
    Calculator configuration settings.

    Manages directory paths, precision settings, input bounds, encoding,
    logging defaults, and auto-save options.
    """

    base_dir: Path
    precision: int
    max_input_value: Decimal
    default_encoding: str
    log_dir: Path
    history_dir: Path
    history_file_name: str
    log_file_name: str
    max_history_size: int
    auto_save: bool

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None,
        log_dir: Optional[Path] = None,
        history_dir: Optional[Path] = None,
        history_file_name: Optional[str] = None,
        log_file_name: Optional[str] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
    ):
        project_root = get_project_root()
        self.base_dir = base_dir or Path(
            os.getenv('CALCULATOR_BASE_DIR', str(project_root))
        ).resolve()

        self.precision = (
            precision if precision is not None 
            else int(os.getenv('CALCULATOR_PRECISION', '10'))
        )

        self.max_input_value = (
            Decimal(str(max_input_value)) if max_input_value is not None 
            else Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e999'))
        )

        self.default_encoding = default_encoding or os.getenv(
            'CALCULATOR_DEFAULT_ENCODING', 'utf-8'
        )

        raw_log_dir = os.getenv('CALCULATOR_LOG_DIR', str(self.base_dir / "logs"))
        self.log_dir = log_dir or Path(raw_log_dir).resolve()

        raw_hist_dir = os.getenv('CALCULATOR_HISTORY_DIR', str(self.base_dir / "history"))
        self.history_dir = history_dir or Path(raw_hist_dir).resolve()

        self.history_file_name = history_file_name or os.getenv(
            'CALCULATOR_HISTORY_FILE', 'history.csv'
        )

        self.log_file_name = log_file_name or os.getenv(
            'CALCULATOR_LOG_FILE', 'app.log'
        )

        self.max_history_size = (
            max_history_size if max_history_size is not None 
            else int(os.getenv('CALCULATOR_MAX_HISTORY_SIZE', '100'))
        )

        if auto_save is not None:
            self.auto_save = auto_save
        else:
            env_auto = os.getenv('CALCULATOR_AUTO_SAVE', 'true').lower()
            self.auto_save = env_auto in ('true', '1', 'yes', 't')

    @property
    def history_file(self) -> Path:
        """Get the full resolved path to the history CSV file."""
        return (self.history_dir / self.history_file_name).resolve()

    @property
    def log_file(self) -> Path:
        """Get the full resolved path to the log file."""
        return (self.log_dir / self.log_file_name).resolve()

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ConfigurationError: If any configuration parameter is invalid.
        """
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")