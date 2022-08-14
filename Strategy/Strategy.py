from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import Portfolio.Portfolio as pf
import Portfolio.PfState as pfstate
import datetime


class Strategy():
    
    @abstractmethod
    def doAlgorithm(self, pf: pf.AbstractPortfolio, data: List, verbose = False):
        pass


######################################
#We implement a command pattern to make the mediation
#Between strategy and portfolio
class StrategyCommandPortfolio(ABC):
    def __init__(self, portfolio: pf.AbstractPortfolio) -> None:
        #we command the portfolio from strategy
        self._portfolio = portfolio

    @property#=getPf=getter
    def pf(self) -> pf.Portfolio:
        return self._pf

    @pf.setter#=setPf
    def pf(self, portfolio: pf.Portfolio) -> None:
        self._pf = portfolio

    @abstractmethod
    def entry(self, time: datetime, listInvestments: dict, verbose = False) -> None:
        pass

    @abstractmethod
    def exit(self, time: datetime, verbose = False) -> None:
        pass


class BacktestCommand(StrategyCommandPortfolio):

    def __init__(self, portfolio: pf.AbstractPortfolio) -> None:
        super().__init__(portfolio)


    def entry(self, time: datetime, listInvestments: dict, verbose = False) -> None:
        if verbose:
            print("We entry the strat.")

        tmpBAL = self._portfolio.getBAL()
        if tmpBAL <= 0:
            if self.pf.getState != "STOPPED":
                self.pf.setState(pfstate.PortfolioIsStopped)
            print("No money in BAL = "+tmpBAL)
            return
        
        for key, quantity in listInvestments.items: #self.pf._children
            if not self.pf.isKeyExists(key):
                newShare = pf.Share(key, quantity)#(key, quantity, time)
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
        self.pf.setState(pfstate.PortfolioIsReady())
        self.pf.notify()#my state is now to position closed


# #Exemple of use
# class Context():
#     """
#     The Context defines the interface of interest to clients.
#     """

#     def __init__(self, strategy: Strategy) -> None:
#         self._strategy = strategy

#     @property
#     def strategy(self) -> Strategy:
#         return self._strategy

#     @strategy.setter
#     def strategy(self, strategy: Strategy) -> None:
#         self._strategy = strategy

#     def do_some_business_logic(self) -> None:
#         print("Context: Sorting data using the strategy (not sure how it'll do it)")
#         result = self._strategy.do_algorithm(["a", "b", "c", "d", "e"])
#         print(",".join(result))

# if __name__ == "__main__":
#     # The client code picks a concrete strategy and passes it to the context.
#     # The client should be aware of the differences between strategies in order
#     # to make the right choice.

#     context = Context(doAlgorithm())
#     print("Client: Strategy is set to normal sorting.")
#     context.do_some_business_logic()
#     print()

#     print("Client: Strategy is set to reverse sorting.")
#     context.strategy = ConcreteStrategyB()
#     context.do_some_business_logic()