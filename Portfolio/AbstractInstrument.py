from __future__ import annotations
from abc import abstractmethod
import string
from typing import List
import datetime
import Portfolio.PfState as st

class AbstractInstrument:

    def __init__(self, _type="currency", _name="generic") -> None:
        self.__type__ = _type
        self.__name__ = _name

    @property
    def parent(self) -> AbstractInstrument:
        return self._parent

    @parent.setter
    def parent(self, parent: AbstractInstrument):
        self._parent = parent

    """
    Return the Type : Portfolio, share, asset, currency etc
    """
    def get_type (self) -> string:
        return self.__type__

    def get_name (self) -> string:
        return self.__name__

    def is_composite(self) -> bool:
        return False

    @abstractmethod
    def set_state(self, state: st.State) -> None:
        pass

    @abstractmethod
    def get_TCV(self) -> float:
        pass
    @abstractmethod
    def set_TCV(self, value: float) -> None:
        pass
    @abstractmethod
    def add_TCV(self, value: float) -> None:
        pass

    #BAL getter setter
    @abstractmethod
    def get_BAL(self) -> float:
        pass
    @abstractmethod
    def set_BAL(self, value: float) -> None:
        pass
    @abstractmethod
    def add_BAL(self, value: float) -> None:
        pass


    @abstractmethod
    def value(self, time: datetime=datetime.date(1970, 1, 1)) -> str:
        """
        Return Value : Portfolio value, Share Value etc
        """
        # pass

    # @abstractmethod
    # def updateMarketQuotation (self,  time: datetime, list_quotations, verbose = False) -> None:
    #     pass

    @abstractmethod
    def is_key_exists (self, key: string) -> bool:
        pass

    @abstractmethod
    def report(self) -> dict:
        pass

# References
# https://refactoring.guru/fr/design-patterns/composite/python/example
