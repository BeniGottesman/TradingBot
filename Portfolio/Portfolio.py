"""Portfolio.py"""

# https://refactoring.guru/fr/design-patterns/composite/python/example

from abc import abstractmethod
import string
from typing import List
from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame
from datetime import date, datetime
from __future__ import annotations


class AbstractInstrument:

    def __init__(self, _type="currency", _name="generic portfolio") -> None:
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
    def value(self) -> str:
        pass
    @abstractmethod
    def updateQuotation (self, listQuotations, verbose = False) -> None:
        pass
    @abstractmethod
    def isKeyExists (key: string) -> bool:
        pass


class AbstractPortfolio(AbstractInstrument):

    def __init__(self, _type="currency", _name="generic portfolio") -> None:
        super().__init__(_type, _name)

    def add(self, component: AbstractPortfolio) -> None:
        pass

    def remove(self, component: AbstractPortfolio) -> None:
        pass

    def is_Composite(self) -> bool:
        return False

class severalPortfolios(AbstractPortfolio):
    """
    The Composite class represents the complex components that may have
    children. Usually, the Composite objects delegate the actual work to their
    children and then "sum-up" the result.
    """

    def __init__(self) -> None:
        self._children: List[AbstractPortfolio] = []

    """
    A composite object can add or remove other components (both simple or
    complex) to or from its child list.
    """

    def add(self, component: AbstractPortfolio) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: AbstractPortfolio) -> None:
        self._children.remove(component)
        component.parent = None

    def is_Composite (self) -> bool:
        return True

    @abstractmethod
    def updateQuotation (self, listQuotations, verbose = False) -> None:
        pass
    @abstractmethod
    def isKeyExists (key: string) -> bool:
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
    def entry(self, time: datetime, listInvestments: dict, listQuotation: dict, verbose = False) -> None:
        pass
    
    def updateValues(self, listQuotations: dict) -> None:
        pass

    @abstractmethod
    def exit(self, time: datetime, listQuotation: dict, verbose = False) -> None:
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
    def entry(self, time: datetime, listInvestments: dict, verbose = False) -> None:
        if verbose:
            print("We entry the strat.")

        tmpBAL = self.pf.getBAL()
        if tmpBAL <= 0:
            print("No money in BAL = "+tmpBAL)
            return
        
        for key, quantity in listInvestments.items: #self.pf._children
            if not self.pf.isKeyExists(key):
                newShare = Share(key, quantity)#(key, quantity, time)
                self.pf.add(newShare)
            else:
                # child.addShareQuantity(time, quantity) and add to a dict
                share = self.pf.getShare(key)
                share.addShareQuantity(quantity)
            tmpBAL -= self.pf.getShare(key).value()

        self.pf.setBAL(tmpBAL)

    def exit(self, time: datetime, verbose = False) -> None:
        if verbose:
            print("We exit the strat.")

        tmpBAL = self.pf.value()
        for key, share in self.pf.getShares().items:
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
# Share = crypto, fx, call, put etc
class Share(AbstractInstrument):
    _state = None
    
    def __init__(self, _name, state: State, _type) -> None:
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

    # @abstractmethod
    # def updateQuotation (self, listQuotations, verbose = False) -> None:
    #     pass
    # @abstractmethod
    # def isKeyExists (key: string) -> bool:
    #     pass

class cryptoCurrency(Share):
    def __init__(self, _name, state: State) -> None:
        _type="cryptoCurrency"
        super().__init__(_type, _name)

    #market value
    def getQuoteCurrentValue (self):
        return self.__QuoteCurrentValue__
    def updateQuotation (self, value, verbose = False) -> None:
        # value = listQuotations[__name__]
        self.__QuoteCurrentValue__ = value

    # method to change the state of the object
    def setState(self, state: State) -> None:
        self._state = state
        self._state.pf = self

    def getPair(self)-> str:
        return "Pair = "+self.__name__

    #return the value hold in $
    def value(self) -> str:
        return self.__QuoteCurrentValue__*self.__numberOfShares__

    def isKeyExists (self, key: string) -> bool:
        if key != __name__:
            return False
        return True

# leaf of share
#here we have a 1 period tree : 1 node + n leafs
class Portfolio(AbstractPortfolio):
    
    #quoteCurrency="USD(T)" usually
    def __init__(self, quoteCurrency: string, portfolioName: string, startingMoney: float) -> None:
        super().__init__("Portfolio", portfolioName)
        self.__Shares__: dict[Share] = {}
        # self.__portfolioName__ = portfolioName
        self.setState(positionClosed())
        self.__quoteCurrency__ = quoteCurrency
        self.__BAL__ = abs(startingMoney)
        self.__TCV__ = abs(startingMoney)

    def setState(self, state: State) -> None:
        self.__state__ = state

    def presentState(self) -> None:
        stateName = self.__state__#string overload operator
        print(f"Portfolio is in {stateName}")

    def getShares(self) -> Share:
        return self.__Shares__

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

    def add(self, share: Share) -> None:
        key = share.getName()
        self.__Shares__ [key] = share
        share.parent = self

    def remove(self, share: Share) -> None:
        key = share.getName()
        self.__Shares__.pop(key, None)
        share.parent = None

    def is_Composite(self) -> bool:
        return False

    def getShare (self, key: string) -> Share:
        if self.__Shares__.has_key(key):
            return self.__Shares__[key]
    # overload operator for []
    def __getitem__(self, key):
        if self.__Shares__.has_key(key):
            return self.__Shares__[key]
    def __setitem__(self, key, value):
        self.__Shares__[key] = value

    def getPortfolioCurrency (self) -> string:
        return self.__quoteCurrency__

    #return the BAL, by induction,
    #it is preferable to updateValues before
    def value(self) -> float:
        tmpValue = 0
        for key, child in self.__Shares__.items:
            tmpValue += child.value()
        return tmpValue
    
    #Update the quote value of the pairs
    def updateQuotation(self, listQuotations, verbose = False) -> None:
        children = self.__Shares__
        for key, value in listQuotations.items: #self.pf._children
            children[key].updateQuotation(value)

    #Search by induction if a key exists
    def isKeyExists (self, key: string) -> bool:
        children = self.__Shares__
        if key in children:
            return True #problem multiple true if by induction
        
        return False

# if __name__ == "__main__":
#     tree = Portfolio()

#     branch1 = Portfolio()
#     branch1.add(Pair())
#     branch1.add(Pair())

#     branch2 = Portfolio()
#     branch2.add(Pair())

#     tree.add(branch1)
#     tree.add(branch2)