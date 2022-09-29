from __future__ import annotations
from abc import ABC, abstractmethod
from random import randrange
from typing import List
import datetime


class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify/Send a report to all observers about an event.
        """
        pass

    @abstractmethod
    def get_report(self, _time: datetime=datetime.date(1970, 1, 1), verbose = False) -> dict:
        """
        Return a report of the strategy
        """
        pass


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass


#References
#https://refactoring.guru/design-patterns/observer/python/example
