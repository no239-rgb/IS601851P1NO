################################################################
#                      Calculator REPL                         #
################################################################

from decimal import Decimal
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.operations import OperationFactory


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands and processing  arithmetic operations.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        print("Calculator started. Type 'help' for commands.")

        while True:
            try:
                # Prompt the user for a command
                command = input("\nEnter command: ").lower().strip()

                if command == 'help':
                    # Display available commands
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root, modulus, integer_division, absolute_difference, percentage - Perform calculations")
                    print("  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    # Exit the REPL loop
                    print("Goodbye!")
                    break

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root','modulus', 'integer_division', 'absolute_difference', 'percentage']:
                    # Perform the specified arithmetic operation
                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print("Operation cancelled")
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print("Operation cancelled")
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            # normalize() removes trailing zeros, :f forces standard string representation
                            result = f"{result.normalize():f}"

                        print(f"\nResult: {result}")
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(f"Error: {e}")
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(f"Unexpected error: {e}")
                    continue

                # Handle unknown commands
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print("\nOperation cancelled")
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"Error: {e}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"Fatal error: {e}")
        raise

