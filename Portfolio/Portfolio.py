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

    def __init__(self, _type="currency", _name="generic portfolio") -> None:
        self.__type__ = _type
        self.__name__ = _name

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

    def getName (self) -> string:
        return self.__name__

    def is_composite(self) -> bool:
        return False

    @abstractmethod
    def value(self) -> str:
        pass
    @abstractmethod
    def updateQuotation (self, listQuotations, verbose = False) -> None:
        pass
    @abstractmethod
    def checkKey (key: string) -> bool:
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

    @property#=getPf=getter
    def pf(self) -> Portfolio:
        return self._pf

    @pf.setter#=setPf
    def pf(self, pf: Portfolio) -> None:
        self._abspf = pf

    #REVOIR LALGO
    def entry(self, listInvestments: dict, verbose = False) -> None:
        if verbose:
            print("We entry the strat.")

        tmpBAL = self.pf.getBAL()
        if tmpBAL <= 0:
            print("No money in BAL = "+tmpBAL)
            return

        #We check if the pairs already exists in pf
        #add checkKey induction method in Portfolio
        exists : List[bool] = []
        children = self.pf.getChildren()
        for key, quantity in listInvestments.items: #self.pf._children
            exists[key] = False
            for i in children:
                child = children [i]
                if child.getName() == key:
                    exists[key] = True
                    break
        
        for key, quantity in listInvestments.items: #self.pf._children
            if not exists[key]:
                newShare = Share(key, quantity)#(key, quantity, time)
                self.pf.add(newShare)
            else:
                # child.addShareQuantity(time, quantity) and add to a dict
                child.addShareQuantity(quantity)
            tmpBAL -= child.value()

        self.pf.setBAL(tmpBAL)

    def exit(self, verbose = False) -> None:
        if verbose:
            print("We exit the strat.")

        tmpBAL = self.pf.value()
        for share in self.pf._children:
            share.setQuantity(0)
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
        super().__init__(_type, _name)
        # self.__name__ = _name #for instance BTCUSDT
        self.setState(state)
        self.__numberOfShares__ = 0
        # self.__BaseCurrentValue__ = 1 because 1 BTC = X Dollar
        self.__QuoteCurrentValue__ = 0 #for 1 BTC = QuoteCurrentValue $

    #market value
    def getQuoteCurrentValue (self):
        return self.__QuoteCurrentValue__
    def updateQuotation (self, value, verbose = False) -> None:
        # value = listQuotations[__name__]
        self.__QuoteCurrentValue__ = value

    def getQuantity (self):
        return self.__numberOfShares__
    def setQuantity (self, quantity: float):
        self.__numberOfShares__ = quantity

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

    def checkKey (self, key: string) -> bool:
        return self.__name__, key == self.__name__

# Composite
class Portfolio(AbstractPortfolio):
    
    #quoteCurrency="USDT" usually
    def __init__(self, quoteCurrency: string, portfolioName: string, startingMoney: float) -> None:
        super().__init__("Portfolio", portfolioName)
        self.__children__: List[AbstractPortfolio] = []
        # self.__portfolioName__ = portfolioName
        self.setState(positionClosed())
        self.__quoteCurrency__ = quoteCurrency
        self.__BAL__ = abs(startingMoney)
        self.__TCV__ = abs(startingMoney)

    def setState(self, state: State) -> None:
        self.__state__ = state

    def getChildren(self) -> AbstractPortfolio:
        return self.__children__

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
        self.__children__.append(abspf)
        abspf.parent = self

    def remove(self, abspf: AbstractPortfolio) -> None:
        self.__children__.remove(abspf)
        abspf.parent = None

    def is_composite(self) -> bool:
        return True

    def getShare (self, key: string) -> AbstractPortfolio:
        for i in len(self.__children__):
            if self.__children__[i].getName() == key:
                return self.__children__[i]
        print("getShare error try catch, key = "+ key)
        sys.exit()

    def getPortfolioCurrency (self) -> string:
        return self.__quoteCurrency__

    #return the BAL, by induction,
    #it is preferable to updateValues before
    def value(self) -> float:
        tmpValue = 0
        for child in self.__children__:
            tmpValue += child.value()
        return tmpValue
    
    #Update the quote value of the pairs
    def updateQuotation(self, listQuotations, verbose = False) -> None:
        for child in self.__children__:
            for key, value in listQuotations.items: #self.pf._children
               if child.getName() == key:
                    child.updateQuotation(value)

    #Search by induction
    def checkKey (self, key: string) -> string, bool:
        for i in len(self.__children__):
            if self.__children__[i].checkKey(key):
                name = self.__children__[i].getName()
                return name, True #problem multiple true if by induction
        
        return name, False

# if __name__ == "__main__":
#     tree = Portfolio()

#     branch1 = Portfolio()
#     branch1.add(Pair())
#     branch1.add(Pair())

#     branch2 = Portfolio()
#     branch2.add(Pair())

#     tree.add(branch1)
#     tree.add(branch2)