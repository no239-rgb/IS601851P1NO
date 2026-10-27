################################################################
#                      Calculator REPL (Command Pattern)       #
################################################################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, List, Optional

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.logger import Logger
from app.operations import OperationFactory


class Command(ABC):
    """Abstract base class for REPL commands (Command Pattern)."""

    @abstractmethod
    def execute(self) -> Any:
        """Execute the command."""
        pass  # pragma: no cover


class CalculateCommand(Command):
    """Command to execute arithmetic calculations."""

    def __init__(self, calculator: Calculator, operation_name: str, a_str: str, b_str: str):
        self.calculator = calculator
        self.operation_name = operation_name
        self.a_str = a_str
        self.b_str = b_str

    def execute(self) -> str:
        operation = OperationFactory.create_operation(self.operation_name)
        self.calculator.set_operation(operation)
        result = self.calculator.perform_operation(self.a_str, self.b_str)

        if isinstance(result, Decimal):
            result = f"{result.normalize():f}"
        return f"\nResult: {result}"


class UndoCommand(Command):
    """Command to revert last calculation."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        self.calculator.undo()
        return "Undo successful."


class RedoCommand(Command):
    """Command to redo last undone calculation."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        self.calculator.redo()
        return "Redo successful."


class HistoryCommand(Command):
    """Command to display calculation history."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        history = self.calculator.get_history()
        if not history:
            return "History is empty."
        lines = ["\nCalculation History:"]
        for idx, calc in enumerate(history, 1):
            lines.append(f"  {idx}. {calc}")
        return "\n".join(lines)


class ClearCommand(Command):
    """Command to clear calculation history."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        self.calculator.clear_history()
        return "History cleared."


class SaveCommand(Command):
    """Command to save calculation history."""

    def __init__(self, calculator: Calculator, file_path: Optional[str] = None):
        self.calculator = calculator
        self.file_path = file_path

    def execute(self) -> str:
        self.calculator.save_history(self.file_path)
        return "History saved successfully."


class LoadCommand(Command):
    """Command to load calculation history."""

    def __init__(self, calculator: Calculator, file_path: Optional[str] = None):
        self.calculator = calculator
        self.file_path = file_path

    def execute(self) -> str:
        self.calculator.load_history(self.file_path)
        return "History loaded successfully."


class HelpCommand(Command):
    """Command to display available commands."""

    def execute(self) -> str:
        lines = [
            "\nAvailable commands:",
            "  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff - Perform calculations",
            "  history - Display calculation history",
            "  clear - Clear calculation history",
            "  undo - Undo the last calculation",
            "  redo - Redo the last undone calculation",
            "  save - Save calculation history to file",
            "  load - Load calculation history from file",
            "  help - Display available commands",
            "  exit - Exit the calculator",
        ]
        return "\n".join(lines)


class CommandInvoker:
    """Invoker class that executes command objects."""

    def execute_command(self, command: Command) -> str:
        return command.execute()


def calculator_repl():
    """
    Command-line interface for the calculator implementing the REPL pattern.
    """
    try:
        config = CalculatorConfig()
        Logger.configure(config)

        calc = Calculator(config)
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        invoker = CommandInvoker()
        print("Calculator started. Type 'help' for commands.")

        calc_commands = [
            'add', 'subtract', 'multiply', 'divide', 'power', 'root',
            'modulus', 'int_divide', 'integer_division',
            'percent', 'percentage', 'abs_diff', 'absolute_difference'
        ]

        while True:
            try:
                command_str = input("\nEnter command: ").lower().strip()

                if command_str == 'help':
                    print(invoker.execute_command(HelpCommand()))
                    continue

                if command_str == 'exit':
                    print("Goodbye!")
                    break

                if command_str in calc_commands:
                    print("\nEnter numbers (or 'cancel' to abort):")
                    a_input = input("First number: ")
                    if a_input.lower() == 'cancel':
                        print("Operation cancelled")
                        continue
                    b_input = input("Second number: ")
                    if b_input.lower() == 'cancel':
                        print("Operation cancelled")
                        continue

                    cmd = CalculateCommand(calc, command_str, a_input, b_input)
                    print(invoker.execute_command(cmd))
                    continue

                if command_str == 'undo':
                    print(invoker.execute_command(UndoCommand(calc)))
                    continue

                if command_str == 'redo':
                    print(invoker.execute_command(RedoCommand(calc)))
                    continue

                if command_str == 'history':
                    print(invoker.execute_command(HistoryCommand(calc)))
                    continue

                if command_str == 'clear':
                    print(invoker.execute_command(ClearCommand(calc)))
                    continue

                if command_str == 'save':
                    print(invoker.execute_command(SaveCommand(calc)))
                    continue

                if command_str == 'load':
                    print(invoker.execute_command(LoadCommand(calc)))
                    continue

                print(f"Unknown command: '{command_str}'. Type 'help' for available commands.")

            except (ValidationError, OperationError) as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                continue
            except EOFError:
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

    except Exception as e:
        print(f"Fatal error: {e}")
        raise


