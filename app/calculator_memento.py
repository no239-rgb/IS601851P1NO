###############################################
#                 Calculator Memento          #
###############################################

from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List

from app.calculation import Calculation


@dataclass
class CalculatorMemento:
    """
    Stores calculator state for undo/redo functionality.
    """

    history: List[Calculation] = field(default_factory=list)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self) -> None:
        """Ensure history is stored as an independent copy."""
        self.history = list(self.history)

    def get_history(self) -> List[Calculation]:
        """Retrieve a defensive copy of saved calculations."""
        return list(self.history)

    def to_dict(self) -> Dict[str, Any]:
        """Convert memento to dictionary representation."""
        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':
        """Create memento from a dictionary representation."""
        return cls(
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp']),
        )
    