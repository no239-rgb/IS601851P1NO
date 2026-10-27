# Enhanced Calculator Command-Line Application

An enterprise-grade, modular command-line calculator built with Python 3.10+. This application combines advanced Object-Oriented Programming (OOP) concepts, robust error handling, data serialization using `pandas`, and six core software design patterns: **Strategy**, **Factory**, **Observer**, **Memento**, **Command**, and **Mixin**.

---

## Project Description

The Enhanced Calculator provides an interactive Read-Eval-Print Loop (REPL) command-line interface supporting fundamental arithmetic and advanced mathematical operations. It maintains a persistent state history, supports full non-destructive Undo/Redo capabilities, auto-saves calculations to CSV format, and writes structured system logs.

### Key Architectural Features & Design Patterns
* **Strategy Pattern**: Encapsulates mathematical execution algorithms into discrete, interchangeable operation classes (`Addition`, `Subtraction`, `Power`, `Root`, etc.) inheriting from an abstract `Operation` base class.
* **Factory Pattern**: Centralizes operation instantiation via `OperationFactory`, decoupling operational lookup keys from concrete class definitions and allowing dynamic runtime registration of new operations.
* **Observer Pattern**: Utilizes an event-driven publisher/subscriber model where the `Calculator` publisher notifies registered subscribers (`LoggingObserver` and `AutoSaveObserver`) whenever a new calculation is executed.
* **Memento Pattern**: Captures immutable snapshots of calculation history state via `CalculatorMemento` with defensive list copying, powering non-destructive `undo` and `redo` operations.
* **Command Pattern**: Encapsulates user requests in the REPL as discrete command objects (`CalculateCommand`, `UndoCommand`, `RedoCommand`, `SaveCommand`, `LoadCommand`, `HelpCommand`, etc.) executed via a central `CommandInvoker`.
* **Mixin Pattern**: Employs `NonZeroDivisorMixin` to inject reusable zero-divisor validation across division-based operation strategies (`Division`, `Modulus`, `IntegerDivision`, `PercentageCalculation`) without duplicating validation logic across classes.
* **Data Serialization**: Leverages `pandas` DataFrames to serialize calculation history to CSV files and deserialize external CSV files back into active state memory.
* **Environment-Based Configuration**: Manages application parameters (directory paths, history bounds, decimal precision, auto-save toggles) via a `.env` configuration file loaded with `python-dotenv`.

---

## Installation Instructions

### Prerequisites
* Python 3.10 or higher
* `git` version control

### Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/no239-rgb/IS601851P1NO
   cd IS601851PNO
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**:
   * **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
   * **Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   * **Windows (PowerShell)**:
     ```powershell
     venv\Scripts\Activate.ps1
     ```

4. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Configuration Setup

The application automatically loads environment variables from a `.env` file located in the project root directory. Default fallback values are provided if `.env` parameters are missing or unspecified.

### Sample `.env` Configuration File

Create a `.env` file in your project root directory with the following structure:

```ini
# Base Directories
CALCULATOR_BASE_DIR=.
CALCULATOR_LOG_DIR=logs
CALCULATOR_HISTORY_DIR=history

# File Settings
CALCULATOR_HISTORY_FILE=history.csv
CALCULATOR_LOG_FILE=app.log
CALCULATOR_DEFAULT_ENCODING=utf-8

# Application Parameters
CALCULATOR_MAX_HISTORY_SIZE=100
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
```

### Configuration Parameters Reference

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `CALCULATOR_BASE_DIR` | Root directory path for relative file resolution | Project Root |
| `CALCULATOR_LOG_DIR` | Directory where log files are stored | `logs/` |
| `CALCULATOR_HISTORY_DIR` | Directory where history CSV files are saved | `history/` |
| `CALCULATOR_HISTORY_FILE` | Filename for history serialization | `history.csv` |
| `CALCULATOR_LOG_FILE` | Filename for application logs | `app.log` |
| `CALCULATOR_DEFAULT_ENCODING`| Text encoding for file I/O operations | `utf-8` |
| `CALCULATOR_MAX_HISTORY_SIZE`| Maximum number of history entries retained in memory | `100` |
| `CALCULATOR_AUTO_SAVE` | Automatically export history to CSV on calculation (`true`/`false`) | `true` |
| `CALCULATOR_PRECISION` | Decimal places for formatted calculation output | `10` |
| `CALCULATOR_MAX_INPUT_VALUE` | Maximum absolute numerical value accepted for inputs | `1e999` |

---

## Usage Guide

Launch the interactive Command-Line Interface (REPL) by running:

```bash
python3 main.py
```

### Supported REPL Commands

#### 1. Arithmetic Operations
Enter any operation command to begin an interactive prompt for two numbers. Type `cancel` during either prompt to abort the operation.

| Command Key | Alias | Operation Description | Example Output |
| :--- | :--- | :--- | :--- |
| `add` | `addition` | Sum of two numbers | `Result: 15` |
| `subtract` | `subtraction` | Difference of two numbers | `Result: 5` |
| `multiply` | `multiplication`| Product of two numbers | `Result: 50` |
| `divide` | `division` | Quotient of two numbers (Zero-divisor protected via Mixin) | `Result: 2` |
| `power` | - | Raises base number to an exponent | `Result: 8` |
| `root` | - | Calculates $n^{\text{th}}$ root of a non-negative number | `Result: 4` |
| `modulus` | - | Remainder of division between two numbers | `Result: 1` |
| `int_divide` | `integer_division`| Quotient truncated to integer | `Result: 3` |
| `percent` | `percentage` | Percentage ratio: $(a / b) \times 100$ | `Result: 25` |
| `abs_diff` | `absolute_difference`| Absolute magnitude of difference: $|a - b|$ | `Result: 5` |

#### 2. History & State Commands

* **`history`**: Displays a numbered list of all calculations recorded in the active session.
* **`undo`**: Reverts the last calculation or action, restoring the previous Memento state.
* **`redo`**: Re-applies the last undone calculation or state transition.
* **`clear`**: Clears all entries from active calculation history.
* **`save`**: Serializes active calculation history to the configured CSV path using `pandas`.
* **`load`**: Deserializes calculation history from the configured CSV path into memory using `pandas`.

#### 3. System Commands

* **`help`**: Displays available commands and usage instructions.
* **`exit`**: Gracefully terminates the REPL interface.

---

## Testing Instructions

The project uses `pytest` for unit testing and `pytest-cov` to enforce code coverage standards. All tests are located in the `tests/` directory.

### Running the Test Suite

Run all unit tests:
```bash
pytest
```

Run unit tests with full terminal coverage reports:
```bash
pytest --cov=app --cov-report=term-missing
```

Run tests and enforce the required 90%+ coverage threshold:
```bash
pytest --cov=app --cov-fail-under=90
```

Generate an HTML code coverage report (`htmlcov/index.html`):
```bash
pytest --cov=app --cov-report=html
```

---

## CI/CD Information

Continuous Integration (CI) is implemented using **GitHub Actions**. The workflow configuration is located in `.github/workflows/python-app.yml`.

### Workflow Lifecycle & Quality Gates
1. **Triggers**: Automated execution runs on every `push` or `pull_request` targeting the `main` branch.
2. **Environment**: Provisions an `ubuntu-latest` virtual runner with Python 3.x.
3. **Dependency Management**: Installs dependencies specified in `requirements.txt`.
4. **Automated Testing & Coverage Gate**: Executes `pytest` with coverage tracking. The pipeline **fails automatically** if total test coverage drops below **90%** (`--cov-fail-under=90`), ensuring high code quality prior to merging.