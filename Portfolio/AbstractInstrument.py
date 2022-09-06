# https://refactoring.guru/fr/design-patterns/composite/python/example

from __future__ import annotations
from abc import abstractmethod
import string
from typing import List
from datetime import datetime
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
    def getType (self) -> string:
        return self.__type__

    def getName (self) -> string:
        return self.__name__

    def is_Composite(self) -> bool:
        return False
    
    @abstractmethod
    def setState(self, state: st.State) -> None:
        pass
    
    @abstractmethod
    def getTCV(self) -> float:
        pass
    @abstractmethod
    def setTCV(self, value: float) -> None:
        pass
    @abstractmethod
    def addTCV(self, value: float) -> None:
        pass

    #BAL getter setter
    @abstractmethod
    def getBAL(self) -> float:
        pass
    @abstractmethod
    def setBAL(self, value: float) -> None:
        pass
    @abstractmethod
    def addBAL(self, value: float) -> None:
        pass


    @abstractmethod
    def value(self) -> str:
        pass
    @abstractmethod
    def updateMarketQuotation (self,  time: datetime, listQuotations, verbose = False) -> None:
        pass
    @abstractmethod
    def isKeyExists (self, key: string) -> bool:
        pass

    @abstractmethod
    def report(self) -> dict:
        pass
