"""Portfolio.py"""

# https://refactoring.guru/fr/design-patterns/composite/python/example

from abc import abstractmethod
import string
from typing import List
import numpy as np
from datetime import datetime
from __future__ import annotations
import designPattern.observer as obs
import Portfolio.PfState as state
import Portfolio.Share as share
import Portfolio.AbstractInstrument as ai

class AbstractPortfolio(ai.AbstractInstrument, obs.Subject):

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
    __observers__: List[obs.Observer] = []

    def attach(self, observer: obs.Observer) -> None:
        print("Subject: Attached an observer.")
        self.__observers__.append(observer)

    def detach(self, observer: obs.Observer) -> None:
        self.__observers__.remove(observer)

    @abstractmethod
    def getWeightArrayOfShares (self) -> np.array:
        pass

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
    # WARNING WHEN USE IT
    def setTCV(self, value: float) -> None:
        if value > self.getTCV():
            self.__TCV__ = value
    def addTCV(self, value: float) -> None:
        self.__TCV__ += value
    # WARNING WHEN USE IT

    def getWeightArrayOfShares (self) -> np.array:
        tmpArray = np.array()
        for pf in self.__portfolios__:
             tmpArray = np.append(tmpArray, pf.getWeightArrayOfShares())
        return tmpArray

    #BAL getter setter
    def getBAL(self) -> float:
        tmpBAL = 0
        for pf in self.__portfolios__:
            tmpBAL += pf.getBAL()
        return tmpBAL
    # WARNING WHEN USE IT
    #LA TCV EVOLUE INDEPENDEMMENT DE LA BAL
    def setBAL(self, value: float) -> None:
        if value > self.getTCV():#SAUF CAS PARTICULIER OU BAL>TCV ...
            self.__BAL__ = value
        self.__BAL__ = value
    def addBAL(self, value: float) -> None:
        self.__BAL__ += value
        tmpTCV = self.getTCV()
        if self.__BAL__ > tmpTCV:
            self.__BAL__ = tmpTCV
    # WARNING WHEN USE IT

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
        tmpDict["TCV"] = self.__BAL__
        tmpDict["BAL"] = self.__TCV__
        
        for i in len(portfolios):
            key = portfolios[i].getName()
            tmpDict[key] = portfolios[i].report()
        return tmpDict

# leaf of share
#here we have a 1 period tree : 1 node + n leafs
class Portfolio(AbstractPortfolio):
    
    #quoteCurrency="USD(T)" usually
    def __init__(self, quoteCurrency: string, portfolioName: string, startingMoney: float) -> None:
        super().__init__("Portfolio", portfolioName)
        self.__Shares__: dict[share.Share] = {}
        self.__numberOfShares__ = 0
        # self.__portfolioName__ = portfolioName
        self.setState(state.PortfolioIsReady())
        self.__quoteCurrency__ = quoteCurrency
        self.__BAL__ = abs(startingMoney)
        self.__TCV__ = abs(startingMoney)

    def setState(self, state: state.State) -> None:
        self.__state__ = state

    def presentState(self) -> None:
        stateName = self.__state__#string overload operator
        print(f"Portfolio is in {stateName}")

    def getShares(self) -> share.Share:
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
    # add two portfolios TCV
    def __add__(self, other): 
        return self.getTCV()+other.getTCV()

    def __str__(self): 
        return "Value of the portfolio = "+self.__TCV__+self.__quoteCurrency__

    def getNumberOfShares(self):
        return self.__numberOfShares__
        
    #add share
    def add(self, share: share.Share) -> None:
        key = share.getName()
        self.__Shares__ [key] = share
        share.parent = self #?
        self.__numberOfShares__ += 1
    #remove share
    def remove(self, share: share.Share) -> None:
        key = share.getName()
        self.__Shares__.pop(key, None)
        share.parent = None #?
        self.__numberOfShares__ -= 1

    def is_Composite(self) -> bool:
        return False

    def getWeightArrayOfShares (self) -> np.array:
        tmpArray = np.array()
        for key, value in self.__Shares__.items:
            qty = value.getShareQuantity()
            tmpArray = np.append(tmpArray, qty)
        return tmpArray

    def getShare (self, key: string) -> share.Share:
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