# https://refactoring.guru/fr/design-patterns/composite/python/example

from abc import abstractmethod
import string
from typing import List
from datetime import datetime
from __future__ import annotations
import Portfolio.PfState as state
import Portfolio.AbstractInstrument as ai


# Leaf
# Share = crypto, fx, call, put etc
class Share(ai.AbstractInstrument):
    _state = None
    
    def __init__(self, _name, _type) -> None:
        super().__init__(_type, _name)
        # self.__name__ = _name #for instance BTCUSDT
        self.setState(state)
        self.__numberOfShares__ = 0
        # self.__BaseCurrentValue__ = 1 because 1 BTC = X Dollar
        self.__quoteCurrentValue__ = 0 #for 1 BTC = QuoteCurrentValue $

    def getShareQuantity (self):
        return self.__numberOfShares__
    def setShareQuantity (self, quantity: float):
        self.__numberOfShares__ = quantity
    def addShareQuantity(self, shareQuantity: float) -> None:
        self.__numberOfShares__ += shareQuantity

    def report(self) -> dict:
        return {self.__numberOfShares__, self.value()}

    # @abstractmethod
    # def updateQuotation (self, listQuotations, verbose = False) -> None:
    #     pass
    # @abstractmethod
    # def isKeyExists (key: string) -> bool:
    #     pass

class cryptoCurrency(Share):
    def __init__(self, _name) -> None:
        _type="cryptoCurrency"
        super().__init__(_type, _name)

    #market value
    def getQuoteCurrentValue (self):
        return self.__QuoteCurrentValue__
    def updateMarketQuotation (self,  time: datetime, value, verbose = False) -> None:
        self.__QuoteCurrentValue__ = value

    def getPair(self)-> str:
        return "Pair = "+self.__name__

    #return the value hold in $
    def value(self) -> str:
        return self.__QuoteCurrentValue__*self.__numberOfShares__

    def isKeyExists (self, key: string) -> bool:
        if key != self.__name__:
            return False
        return True
