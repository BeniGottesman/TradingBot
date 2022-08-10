"""Portfolio.py"""

# https://refactoring.guru/fr/design-patterns/composite/python/example

from abc import abstractmethod
import string
import sys
from typing import List
from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame
import BinanceClient
from datetime import date
from __future__ import annotations


class AbstractPortfolio:

    def __init__(self, _type="currency") -> None:
        self.__type__ = _type

    @property
    def parent(self) -> AbstractPortfolio:
        return self._parent

    @parent.setter
    def parent(self, parent: AbstractPortfolio):
        self._parent = parent

    def add(self, component: AbstractPortfolio) -> None:
        pass

    def remove(self, component: AbstractPortfolio) -> None:
        pass

    """
    Return the Type : Portfolio, share, asset, currency etc
    """
    def getType (self) -> string:
        return self.__type__

    def is_composite(self) -> bool:
        return False

    def value(self) -> str:
        pass

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class State():
    @property#=getPf=getter
    def pf(self) -> AbstractPortfolio:
        return self._abspf

    @pf.setter#=setPf
    def pf(self, abspf: AbstractPortfolio) -> None:
        self._abspf = abspf

    @abstractmethod
    def entry(self, listInvestments: dict, listQuotation: dict, verbose = False) -> None:
        pass
    
    def updateValues(self, listQuotations: dict) -> None:
        pass

    @abstractmethod
    def exit(self, listQuotation: dict, verbose = False) -> None:
        pass

    @abstractmethod
    def myStateIs (self) -> None:
        pass

# The common state interface for all the states
class LongPortfolio(State):

    def entry(self, listInvestments: dict, listQuotation: dict, verbose = False) -> None:
        if verbose:
            print("We entry the strat.")

        if self.pf.BAL <= 0:
            print("No money in BAL.")
            return

        for key, quantity in listInvestments.items: #self.pf._children
            child = self.pf._children
            if not key in child:
                newShare = Share(key, quantity)
                self.pf.add(newShare)
            else:
                child.addQuantity(quantity)
            self.pf.BAL -= quantity*listQuotation[key]

    def updateValues(self, listQuotations: dict, verbose = False) -> None:
        self.pf.TCV = 0
        for key, value in listQuotations.items: #self.pf._children
            share = self.pf.getShare(key)
            self.pf.TCV += share.getQuantity()*value
        if verbose:
            print("Portfolio Value "+self.pf.TCV)

    def exit(self, listQuotation: dict, verbose = False) -> None:
        if verbose:
            print("We exit the strat.")
        
        for key, tmp in listQuotation.items: #self.pf._children
            share = self.pf.getLeaf(key)
            self.pf.BAL += share.getQuantity()*listQuotation[key]
            self.pf.remove(key)
        self.pf.TCV = self.pf.BAL

    def myStateIs (self) -> None:
        _type = self._abspf.getType()
        print("The "+_type+" is Long")

class ShortPortfolio (State):
    def entry(self) -> None:
        print("we entry the strat")

    def exit(self) -> None:
        print("we exit the strat")

    def myStateIs (self) -> None:
        _type = self._abspf.getType()
        print("The "+_type+" is Short")

class Nothing(State):
    def entry(self) -> None:
        print("Entry : Actually No Strat")

    def exit(self) -> None:
        print("Exit : Actually No Strat")

    def myStateIs (self) -> None:
        _type = self._abspf.getType()
        print("myStateIs : Actually No Strat with "+_type)

# Leaf
class Share(AbstractPortfolio):
    _state = None

    #_type="currency"
    def __init__(self, _name, state: State, _type="currency") -> None:
        super().__init__(_type)
        self.__name__ = _name #for instance BTCUSDT
        self.setState(state)
        self.numberOfShares = 0
        self.BaseCurrentValue = 0
        self.QuoteCurrentValue = 0

    def getQuantity (self):
        return self.numberOfShares
    def setQuantity (self, quantity: float):
        self.numberOfShares = quantity

    def getName (self):
        return self.__name__

    # method to change the state of the object
    def setState(self, state: State) -> None:
        self._state = state
        self._state.pf = self

    def presentState(self) -> None:
        print(f"Portfolio is in {type(self._state).__name__}")

    def getPair(self)-> str:
        return "Pair = "+self.__name__

    def value(self) -> str:
        return self.QuoteCurrentValue

# Composite
class Portfolio(AbstractPortfolio):
    
    #quoteCurrency="USDT" usually
    def __init__(self, quoteCurrency: string, state: State, portfolioName: string) -> None:
        super().__init__("Portfolio")
        self._children: List[AbstractPortfolio] = []
        self.__portfolioName__ = portfolioName
        self.setState(state)
        self._quoteCurrency = quoteCurrency

    def add(self, abspf: AbstractPortfolio) -> None:
        self._children.append(abspf)
        abspf.parent = self

    def remove(self, abspf: AbstractPortfolio) -> None:
        self._children.remove(abspf)
        abspf.parent = None

    def is_composite(self) -> bool:
        return True

    def getType (self) -> string:
        return self.__type__

    def getShare (self, key: string) -> AbstractPortfolio:
        for i in len(self._children):
            if self._children[i].getName() == key:
                return self._children[i]
        print("getShare error try catch, key = "+ key)
        sys.exit()

    def getPortfolioCurrency (self) -> string:
        return self._quoteCurrency

    def value(self) -> str:
        self.TCV = 0
        for child in self._children:
            self.TCV += child.value()
        return self.TCV

# if __name__ == "__main__":
#     tree = Portfolio()

#     branch1 = Portfolio()
#     branch1.add(Pair())
#     branch1.add(Pair())

#     branch2 = Portfolio()
#     branch2.add(Pair())

#     tree.add(branch1)
#     tree.add(branch2)