import datetime
from decimal import Decimal
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def test_memento_initialization_defaults():
    """Verify default initialization of CalculatorMemento."""
    memento = CalculatorMemento()
    assert memento.history == []
    assert isinstance(memento.timestamp, datetime.datetime)


def test_memento_defensive_copy_on_init():
    """Verify modifying original history list does not mutate memento state."""
    calc1 = Calculation(operation="add", operand1=Decimal("5"), operand2=Decimal("3"))
    original_list = [calc1]

    memento = CalculatorMemento(history=original_list)
    original_list.append(
        Calculation(operation="subtract", operand1=Decimal("10"), operand2=Decimal("2"))
    )

    assert len(memento.history) == 1
    assert memento.history[0] == calc1


def test_memento_get_history_defensive_copy():
    """Verify get_history returns an independent list copy."""
    calc1 = Calculation(operation="add", operand1=Decimal("2"), operand2=Decimal("2"))
    memento = CalculatorMemento(history=[calc1])

    retrieved = memento.get_history()
    retrieved.clear()

    assert len(memento.get_history()) == 1


def test_memento_to_dict_and_from_dict_roundtrip():
    """Verify dictionary serialization and deserialization."""
    fixed_time = datetime.datetime(2026, 10, 27, 12, 0, 0)
    calc = Calculation(operation="multiply", operand1=Decimal("4"), operand2=Decimal("5"))
    memento = CalculatorMemento(history=[calc], timestamp=fixed_time)

    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)

    assert restored.timestamp == fixed_time
    assert len(restored.history) == 1
    assert restored.history[0].operation == "multiply"