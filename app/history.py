########################
# History Management    #
########################

from abc import ABC, abstractmethod
from typing import Any
from app.calculation import Calculation
from app.logger import Logger


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """Handle new calculation event."""
        pass  # pragma: no cover


class LoggingObserver(HistoryObserver):
    """
    Observer that logs calculations to the system log via Logger.
    """

    def update(self, calculation: Calculation) -> None:
        """Log calculation details upon notification."""
        if calculation is None:
            raise AttributeError("Calculation cannot be None")

        Logger.log_calculation(calculation)


class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculation history.
    """

    def __init__(self, calculator: Any):
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        """Trigger auto-save if enabled in configuration."""
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            Logger.info("History auto-saved")
