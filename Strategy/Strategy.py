from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import Portfolio.Portfolio as pf
import Portfolio.PfState as pfstate
import datetime


class Strategy():
    @abstractmethod
    def do_algorithm(self, portfolio: pf.AbstractPortfolio, data: List, verbose = False):
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
        return self._portfolio

    @pf.setter#=setPf
    def pf(self, portfolio: pf.Portfolio) -> None:
        self._pf = portfolio

    @abstractmethod
    def entry(self, time: datetime, list_investments: dict, verbose = False) -> None:
        pass

    @abstractmethod
    def exit(self, time: datetime, verbose = False) -> None:
        pass


class BacktestCommand(StrategyCommandPortfolio):
    #Useless
    # def __init__(self, portfolio: pf.AbstractPortfolio) -> None:
    #     super().__init__(portfolio)


    def entry(self, time: datetime, list_investments: dict, verbose = False) -> None:
        if verbose:
            print("We entry the strat.")

        tmp_balance = self._portfolio.get_BAL()
        if tmp_balance <= 0:
            if self.pf.getState() != "STOPPED":
                self.pf.set_state(pfstate.PortfolioIsStopped())# PROBLEM
            print("No money in BAL = "+str(tmp_balance))
            return

        for key, quantity in list_investments.items(): #self.pf._children
            if not self.pf.is_key_exists(key):
                new_share = pf.Share(key, quantity)#(key, quantity, time)
                self.pf.add_share(new_share)
            else:
                # child.addShareQuantity(time, quantity) and add to a dict
                share = self.pf.get_share(key)
                share.add_share_quantity(quantity)
            tmp_balance -= self.pf.get_share(key).value(time)

        self.pf.set_BAL(tmp_balance)
        self.pf.notify()#each time we notify we send the pf

    def exit(self, time: datetime, verbose = False) -> None:
        if verbose:
            print("We exit the strat.")

        tmp_balance = self.pf.value(time)
        shares=self.pf.get_shares()
        for key in shares.keys():
            shares[key].setShareQuantity(0)
        self.pf.set_TCV (tmp_balance)
        self.pf.set_BAL (tmp_balance)

        #ATTENTION CHECK IF IT IS GOOD
        self.pf.set_state(pfstate.PortfolioIsReady())
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
