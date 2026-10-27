########################
# Logger Infrastructure #
########################

import logging
from pathlib import Path
from typing import Any, Optional


class Logger:
    """
    Centralized logging infrastructure manager.

    Handles log directory creation, configures file handlers using settings from
    CalculatorConfig, and provides standardized static methods for recording events.
    """

    _configured: bool = False

    @classmethod
    def configure(cls, config: Optional[Any] = None) -> None:
        """
        Configure application-wide logging handlers and log file path.

        Args:
            config (Optional[Any]): CalculatorConfig instance.
        """
        if config and hasattr(config, "log_dir"):
            log_dir = Path(config.log_dir).resolve()
            log_file_name = getattr(config, "log_file_name", "app.log")
        else:
            log_dir = Path("logs").resolve()
            log_file_name = "app.log"

        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / log_file_name

        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            force=True,
        )
        cls._configured = True

    @staticmethod
    def info(message: str) -> None:
        """Log an informational message."""
        logging.info(message)

    @staticmethod
    def warning(message: str) -> None:
        """Log a warning message."""
        logging.warning(message)

    @staticmethod
    def error(message: str) -> None:
        """Log an error message."""
        logging.error(message)

    @classmethod
    def log_calculation(cls, calculation: Any) -> None:
        """
        Format and log calculation details.

        Args:
            calculation (Any): Calculation instance to be logged.

        Raises:
            AttributeError: If calculation is None.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")

        cls.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = {calculation.result}"
        )
