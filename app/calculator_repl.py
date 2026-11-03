# ==============================================================================
# REPLACE ENTIRE CONTENT OF app/calculator_repl.py:
# ==============================================================================
################################################################
#                      Calculator REPL (Command Pattern)       #
################################################################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, List, Optional
import colorama
from colorama import Fore, Style

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.logger import Logger
from app.operations import OperationFactory

# Initialize colorama for cross-platform color support
colorama.init(autoreset=True)


class Command(ABC):
    """Abstract base class for REPL commands (Command Pattern)."""

    @abstractmethod
    def execute(self) -> Any:
        """Execute the command."""
        pass  # pragma: no cover


class CommandDecorator(Command):
    """Base Decorator for Command objects (Decorator Design Pattern)."""

    def __init__(self, command: Command):
        self._command = command

    def execute(self) -> Any:
        return self._command.execute()


class DynamicHelpDecorator(CommandDecorator):
    """
    Decorator Design Pattern implementation that dynamically enhances the 
    help menu with available operations from OperationFactory and color formatting.
    """

    def execute(self) -> str:
        base_text = self._command.execute()
        operations = ", ".join(OperationFactory.get_primary_operations())
        op_line = f"  {operations} - Perform calculations"

        header = f"{Fore.CYAN}\nAvailable commands:{Style.RESET_ALL}"
        op_entry = f"{Fore.GREEN}{op_line}{Style.RESET_ALL}"

        base_lines = base_text.split("\n")
        colored_base = [f"{Fore.GREEN}{line}{Style.RESET_ALL}" for line in base_lines if line.strip()]

        return "\n".join([header, op_entry] + colored_base)


class CalculateCommand(Command):
    """Command to execute arithmetic calculations with configured precision formatting."""

    def __init__(self, calculator: Calculator, operation_name: str, a_str: str, b_str: str):
        self.calculator = calculator
        self.operation_name = operation_name
        self.a_str = a_str
        self.b_str = b_str

    def execute(self) -> str:
        operation = OperationFactory.create_operation(self.operation_name)
        self.calculator.set_operation(operation)
        result = self.calculator.perform_operation(self.a_str, self.b_str)

        if self.calculator.history:
            latest_calc = self.calculator.history[-1]
            raw_formatted = latest_calc.format_result(self.calculator.config.precision)
            formatted_result = f"{Decimal(raw_formatted):f}"
            return f"\n{Fore.GREEN}Result: {formatted_result}{Style.RESET_ALL}"

        if isinstance(result, Decimal):
            result = f"{result.normalize():f}"
        return f"\n{Fore.GREEN}Result: {result}{Style.RESET_ALL}"


class UndoCommand(Command):
    """Command to revert last calculation."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        self.calculator.undo()
        return f"{Fore.GREEN}Undo successful.{Style.RESET_ALL}"


class RedoCommand(Command):
    """Command to redo last undone calculation."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        self.calculator.redo()
        return f"{Fore.GREEN}Redo successful.{Style.RESET_ALL}"


class HistoryCommand(Command):
    """Command to display calculation history."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        history = self.calculator.get_history()
        if not history:
            return f"{Fore.YELLOW}History is empty.{Style.RESET_ALL}"
        lines = [f"{Fore.CYAN}\nCalculation History:{Style.RESET_ALL}"]
        for idx, calc in enumerate(history, 1):
            lines.append(f"  {idx}. {calc}")
        return "\n".join(lines)


class ClearCommand(Command):
    """Command to clear calculation history."""

    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def execute(self) -> str:
        self.calculator.clear_history()
        return f"{Fore.GREEN}History cleared.{Style.RESET_ALL}"


class SaveCommand(Command):
    """Command to save calculation history."""

    def __init__(self, calculator: Calculator, file_path: Optional[str] = None):
        self.calculator = calculator
        self.file_path = file_path

    def execute(self) -> str:
        self.calculator.save_history(self.file_path)
        return f"{Fore.GREEN}History saved successfully.{Style.RESET_ALL}"


class LoadCommand(Command):
    """Command to load calculation history."""

    def __init__(self, calculator: Calculator, file_path: Optional[str] = None):
        self.calculator = calculator
        self.file_path = file_path

    def execute(self) -> str:
        self.calculator.load_history(self.file_path)
        return f"{Fore.GREEN}History loaded successfully.{Style.RESET_ALL}"


class HelpCommand(Command):
    """Base command returning non-operational CLI instructions."""

    def execute(self) -> str:
        lines = [
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
        print(f"{Fore.CYAN}Calculator started. Type 'help' for commands.{Style.RESET_ALL}")

        calc_commands = OperationFactory.get_available_operations()

        while True:
            try:
                command_str = input("\nEnter command: ").lower().strip()

                if command_str == 'help':
                    help_cmd = DynamicHelpDecorator(HelpCommand())
                    print(invoker.execute_command(help_cmd))
                    continue

                if command_str == 'exit':
                    print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                    break

                if command_str in calc_commands:
                    print(f"{Fore.CYAN}\nEnter numbers (or 'cancel' to abort):{Style.RESET_ALL}")
                    a_input = input("First number: ")
                    if a_input.lower() == 'cancel':
                        print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                        continue
                    b_input = input("Second number: ")
                    if b_input.lower() == 'cancel':
                        print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
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

                print(f"{Fore.RED}Unknown command: '{command_str}'. Type 'help' for available commands.{Style.RESET_ALL}")

            except (ValidationError, OperationError) as e:
                Logger.error(f"Calculation error: {e}")
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                continue
            except EOFError:
                print(f"\n{Fore.CYAN}Input terminated. Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                Logger.error(f"Unexpected REPL error: {e}")
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                continue

    except Exception as e:
        Logger.error(f"Fatal REPL error: {e}")
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        raise