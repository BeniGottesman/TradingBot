#See https://refactoring.guru/fr/design-patterns/memento/python/example
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

class Memento(ABC):
    """
    The Memento interface provides a way to retrieve the memento's metadata,
    such as creation date or name. However, it doesn't expose the Originator's
    state.
    """
    def __init__(self, content):
        """put all your file content here"""
        self.content = content

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_date(self) -> str:
        pass


class ConcreteMemento(Memento):
    def __init__(self, timeStrat: datetime, state: dict) -> None:
        self._state = state
        self._time_strategy = timeStrat # Strategy time
        self._date = str(datetime.now())[:19] # Computer time

    def get_state(self) -> dict:
        """
        The Originator uses this method when restoring its state.
        """
        return self._state

    def get_name(self) -> str:
        """
        The rest of the methods are used by the Caretaker to display metadata.
        """
        return f"{self._date}-{self._time_strategy} / ({self._state[0:1]}...)"

    def get_date(self) -> str:
        return self._date
