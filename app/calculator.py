########################
# Calculator Class     #
########################

from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation

Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]


class Calculator:
    """
    Main calculator class implementing Strategy, Observer, Memento, and Factory patterns.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        if config is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        self.operation_strategy: Optional[Operation] = None
        self.history: List[Calculation] = []
        self.observers: List[HistoryObserver] = []
        self._undo_stack: List[CalculatorMemento] = []
        self._redo_stack: List[CalculatorMemento] = []

    def set_operation(self, operation: Operation) -> None:
        """Set the current operation strategy."""
        self.operation_strategy = operation

    def add_observer(self, observer: HistoryObserver) -> None:
        """Register an observer."""
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer: HistoryObserver) -> None:
        """Remove a registered observer."""
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, calculation: Calculation) -> None:
        """Notify registered observers of a calculation event."""
        for observer in self.observers:
            observer.update(calculation)

    def save_undo_snapshot(self) -> None:
        """Save a state snapshot to the undo stack and reset redo history."""
        self._undo_stack.append(CalculatorMemento(history=self.history))
        self._redo_stack.clear()

    def perform_operation(
        self,
        a: Union[str, Number],
        b: Union[str, Number]
    ) -> CalculationResult:
        """
        Perform calculation with current operation strategy and update state.
        """
        if not self.operation_strategy:
            raise OperationError("No operation set")

        try:
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            result = self.operation_strategy.execute(validated_a, validated_b)
            calc_obj = Calculation(
                operation=str(self.operation_strategy),
                operand1=validated_a,
                operand2=validated_b
            )

            self.save_undo_snapshot()
            self.history.append(calc_obj)

            if len(self.history) > self.config.max_history_size:
                self.history = self.history[-self.config.max_history_size:]

            self.notify_observers(calc_obj)
            return result

        except ValidationError:
            raise
        except Exception as e:
            raise OperationError(f"Operation failed: {str(e)}")

    def undo(self) -> bool:
        """Revert the last calculation using Memento state."""
        if not self._undo_stack:
            raise OperationError("No operations to undo")

        self._redo_stack.append(CalculatorMemento(history=self.history))
        previous_memento = self._undo_stack.pop()
        self.history = previous_memento.get_history()
        return True

    def redo(self) -> bool:
        """Redo the last undone calculation using Memento state."""
        if not self._redo_stack:
            raise OperationError("No operations to redo")

        self._undo_stack.append(CalculatorMemento(history=self.history))
        next_memento = self._redo_stack.pop()
        self.history = next_memento.get_history()
        return True

    def clear_history(self) -> None:
        """Clear calculation history."""
        self.save_undo_snapshot()
        self.history.clear()

    def get_history(self) -> List[Calculation]:
        """Return a copy of calculation history."""
        return list(self.history)

    def save_history(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """Save history to a CSV file using pandas."""
        target_path = Path(file_path).resolve() if file_path else self.config.history_file
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            records = [calc.to_dict() for calc in self.history]
            df = pd.DataFrame(records, columns=['operation', 'operand1', 'operand2', 'result', 'timestamp'])
            df.to_csv(target_path, index=False, encoding=self.config.default_encoding)
        except Exception as e:
            raise OperationError(f"Failed to save history: {str(e)}")

    def load_history(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """Load history from a CSV file using pandas."""
        target_path = Path(file_path).resolve() if file_path else self.config.history_file
        if not target_path.exists():
            raise OperationError(f"History file not found: {target_path}")

        try:
            df = pd.read_csv(target_path, encoding=self.config.default_encoding)
            if df.empty:
                self.save_undo_snapshot()
                self.history.clear()
                return

            required_cols = {'operation', 'operand1', 'operand2', 'result', 'timestamp'}
            if not required_cols.issubset(set(df.columns)):
                raise ValidationError("Malformed CSV file: missing required columns")

            loaded_history: List[Calculation] = []
            for _, row in df.iterrows():
                calc_dict = {
                    'operation': str(row['operation']),
                    'operand1': str(row['operand1']),
                    'operand2': str(row['operand2']),
                    'result': str(row['result']),
                    'timestamp': str(row['timestamp']),
                }
                loaded_history.append(Calculation.from_dict(calc_dict))

            self.save_undo_snapshot()
            self.history = loaded_history

        except (ValidationError, OperationError):
            raise
        except Exception as e:
            raise OperationError(f"Failed to load history: {str(e)}")


        

