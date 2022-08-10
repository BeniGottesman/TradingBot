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

    @abstractmethod
    def __str__(self): 
        pass

# The common state interface for all the states
class readyToTrade(State):

    def entry(self, listInvestments: dict, listQuotation: dict, verbose = False) -> None:
        if verbose:
            print("We entry the strat.")

        tmpBAL = self.pf.getBAL()
        if tmpBAL <= 0:
            print("No money in BAL = "+tmpBAL)
            return

        for key, quantity in listInvestments.items: #self.pf._children
            child = self.pf._children
            if not key in child:
                newShare = Share(key, quantity)
                self.pf.add(newShare)
            else:
                child.addShareQuantity(quantity)
            tmpBAL -= quantity*listQuotation[key]

        self.pf.setBAL(tmpBAL)

    def exit(self, listQuotation: dict, verbose = False) -> None:
        if verbose:
            print("We exit the strat.")

        tmpBAL = self.pf.getBAL()
        for key, tmp in listQuotation.items: #self.pf._children
            share = self.pf.getLeaf(key)
            tmpBAL += share.getQuantity()*listQuotation[key]
            share.setQuantity(0) #or we remove
            # self.pf.remove(key)
        self.pf.setTCV (tmpBAL)
        self.pf.setBAL (tmpBAL)

        #ATTENTION CHECK IF IT IS GOOD
        self.pf.setState(positionClosed())

    @abstractmethod
    def myStateIs (self) -> None:
        pass

class LongPortfolio(readyToTrade):
    def myStateIs (self) -> None:
        _type = self._abspf.getType()
        print("The "+_type+" is Long")

    def __str__(self): 
        return "Long"

class ShortPortfolio(readyToTrade):
    def myStateIs (self) -> None:
        _type = self._abspf.getType()
        print("The "+_type+" is Short")

    def __str__(self): 
        return "Short"

class positionClosed(State):
    def entry(self) -> None:
        print("Entry : Actually No Strat")

    def exit(self) -> None:
        print("Exit : Actually No Strat")

    def myStateIs (self) -> None:
        _type = self._abspf.getType()
        print("myStateIs : Actually No Strat with "+_type)

    def __str__(self): 
        return "No Position"

# Leaf
class Share(AbstractPortfolio):
    _state = None

    #_type="currency"
    def __init__(self, _name, state: State, _type="currency") -> None:
        super().__init__(_type)
        self.__name__ = _name #for instance BTCUSDT
        self.setState(state)
        self.__numberOfShares__ = 0
        # self.__BaseCurrentValue__ = 1 because 1 BTC = X Dollar
        self.__QuoteCurrentValue__ = 0 #for 1 BTC = QuoteCurrentValue $

    #market value
    def getQuoteCurrentValue (self):
        return self.__QuoteCurrentValue__
    def setQuoteCurrentValue (self, value: float):
        self.__QuoteCurrentValue__ = value

    def getQuantity (self):
        return self.__numberOfShares__
    def setQuantity (self, quantity: float):
        self.__numberOfShares__ = quantity

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

    #return the value hold in $
    def value(self) -> str:
        return self.__QuoteCurrentValue__*self.__numberOfShares__

    def addShareQuantity(self, shareQuantity: float) -> None:
        self.__numberOfShares__ += shareQuantity

# Composite
class Portfolio(AbstractPortfolio):
    
    #quoteCurrency="USDT" usually
    def __init__(self, quoteCurrency: string, portfolioName: string, startingMoney: float) -> None:
        super().__init__("Portfolio")
        self._children: List[AbstractPortfolio] = []
        self.__portfolioName__ = portfolioName
        self.setState(positionClosed())
        self.__quoteCurrency__ = quoteCurrency
        self.__BAL__ = abs(startingMoney)
        self.__TCV__ = abs(startingMoney)

    def setState(self, state: State) -> None:
        self.__state__ = state

    #TCV getter setter
    def getTCV(self) -> float:
        return self.__TCV__
    def setTCV(self, value: float) -> None:
        self.__TCV__ = value
    def addTCV(self, value: float) -> None:
        self.__TCV__ += value

    #BAL getter setter
    def getBAL(self) -> float:
        return self.__BAL__
    def setBAL(self, value: float) -> None:
        self.__BAL__ = value
    def addBAL(self, value: float) -> None:
        self.__BAL__ += value

    # operator overloading
    # add two portfolios
    def __add__(self, other): 
        return self.getTCV()+other.getTCV()

    def __str__(self): 
        return "Value of the portfolio = "+self.__TCV__+self.__quoteCurrency__

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
        return self.__quoteCurrency__

    #return the TCV, by induction,
    #it is preferable to updateValues before
    def value(self) -> str:
        self.__TCV__ = 0
        for child in self._children:
            self.__TCV__ += child.value()
        return self.__TCV__
    
    #Update the quote value of the pairs
    def updateValues(self, listQuotations: dict, verbose = False) -> None:

        for child in self._children:
            for key, value in listQuotations.items: #self.pf._children
               if child.getName() == key:
                    child.setQuoteCurrentValue(value)

# if __name__ == "__main__":
#     tree = Portfolio()

#     branch1 = Portfolio()
#     branch1.add(Pair())
#     branch1.add(Pair())

#     branch2 = Portfolio()
#     branch2.add(Pair())

#     tree.add(branch1)
#     tree.add(branch2)