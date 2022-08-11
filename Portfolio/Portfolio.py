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

#For importing observer pattern
import sys
import os
path = os.path.abspath(os.getcwd())
path = os.path.abspath(os.path.dirname(path))+"\designPattern\\"
sys.path.insert(1, path)
import observer

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

class AbstractPortfolio(AbstractInstrument, Subject):

    def __init__(self, _type="currency", _name="generic portfolio") -> None:
        super().__init__(_type, _name)

    def add(self, component: AbstractPortfolio) -> None:
        pass

    def remove(self, component: AbstractPortfolio) -> None:
        pass

    def is_Composite(self) -> bool:
        return False

    """
    Observer    
    """
    # _state: int = None
    __observers__: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self.__observers__.append(observer)

    def detach(self, observer: Observer) -> None:
        self.__observers__.remove(observer)

    @abstractmethod
    def notify(self, verbose = False) -> None:        
        pass
    @abstractmethod
    def report(self, verbose = False) -> dict:       
        pass
    

class severalPortfolios(AbstractPortfolio):

    def __init__(self) -> None:
        self.__portfolios__: List[AbstractPortfolio] = []
        self.__TCV__ = 0
        self.__BAL__ = 0

    def add(self, portfolio: AbstractPortfolio) -> None:
        self.__portfolios__.append(portfolio)
        self.__TCV__ = self.getTCV()
        portfolio.parent = self

    def remove(self, porfolio: AbstractPortfolio) -> None:
        self.__TCV__ -= self.getTCV()
        self.__portfolios__.remove(porfolio)
        porfolio.parent = None

    #TCV getter setter
    def getTCV(self) -> float:
        tmpTCV = 0
        for pf in self.__portfolios__:
            tmpTCV += pf.getTCV()
        return tmpTCV
    def setTCV(self, value: float) -> None:
        if value > self.getTCV():
            self.__TCV__ = value
    def addTCV(self, value: float) -> None:
        self.__TCV__ += value

    #BAL getter setter
    def getBAL(self) -> float:
        tmpBAL = 0
        for pf in self.__portfolios__:
            tmpBAL += pf.getBAL()
        return tmpBAL
    def setBAL(self, value: float) -> None:
        if value > self.getTCV():
            self.__BAL__ = value
        self.__BAL__ = value
    def addBAL(self, value: float) -> None:
        self.__BAL__ += value
        tmpTCV = self.getTCV()
        if self.__BAL__ > tmpTCV:
            self.__BAL__ = tmpTCV

    def is_Composite (self) -> bool:
        return True

    def notify(self, verbose = False) -> None:
        if verbose:
            print("Subject: Notifying observers...")
        for observer in self.__observers__:
            observer.update(self)

    def updateMarketQuotation (self,  time: datetime, listQuotations, verbose = False) -> None:
        portfolios = self.__portfolios__
        self.__timeNow__ = time
        for i in len(portfolios):
            portfolios[i].updateMarketQuotation(self, time, listQuotations)

    def isKeyExists (self, key: string) -> bool:
        portfolios = self.__portfolios__
        for i in len(portfolios):
            portfolios[i].isKeyExists(key)

    def report(self) -> dict:
        portfolios = self.__portfolios__
        tmpDict = {}
        tmpDict["time"] = self.__timeNow__
        for i in len(portfolios):
            key = portfolios[i].getName()
            tmpDict[key] = portfolios[i].report()
        return tmpDict

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class State():

    '''
    getter and setter
    '''
    @property#=getPf=getter
    def pf(self) -> AbstractPortfolio:
        return self._abspf
    @pf.setter#=setPf
    def pf(self, abspf: AbstractPortfolio) -> None:
        self._abspf = abspf
    '''
    getter and setter
    '''

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
        self.pf.notify()#each time we notify we send the pf

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
        self.pf.notify()#my state is now to position closed

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

    def report(self) -> dict:
        return {self.__numberOfShares__, self.value()}

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
    def updateMarketQuotation(self, time: datetime, listQuotations, verbose = False) -> None:
        children = self.__Shares__
        for key, value in listQuotations.items: #self.pf._children
            if self.isKeyExists:
                children[key].updateQuotation(time, value)

    #Search by induction if a key exists
    def isKeyExists (self, key: string) -> bool:
        children = self.__Shares__
        if key in children:
            return True #problem multiple true if by induction
        return False

    def report(self) -> dict:
        children = self.__Shares__
        tmpDict = {}
        tmpDict["TCV"] = self.__TCV__
        tmpDict["BAL"] = self.__BAL__
        for key, child in children.items:
            tmpDict[key] = child.report()
        return tmpDict

# if __name__ == "__main__":
#     tree = Portfolio()

#     branch1 = Portfolio()
#     branch1.add(Pair())
#     branch1.add(Pair())

#     branch2 = Portfolio()
#     branch2.add(Pair())

#     tree.add(branch1)
#     tree.add(branch2)