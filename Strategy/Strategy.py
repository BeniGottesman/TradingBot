from __future__ import annotations
from abc import ABC, abstractmethod
import datetime
from typing import List
import Portfolio.portfolio as pf
import Portfolio.portfolio_state as pfstate
import designPattern.observer as obs


class Strategy(obs.Subject):
    def __init__(self):
        self.__strategy_report__: dict = {}

    @abstractmethod
    def do_strategy(self, portfolio: pf.AbstractPortfolio, data: List, verbose = False):
        """
        Start the strategy.
        """
        pass

    ##################################
    #########Observer Pattern#########
    __observers__: List[obs.Observer] = []

    def attach(self, observer: obs.Observer) -> None:
        print("Subject: Attached an observer to strategy.")
        self.__observers__.append(observer)

    def detach(self, observer: obs.Observer) -> None:
        self.__observers__.remove(observer)

    def notify(self, verbose = False) -> None:
        """
        Notify/Send a report to all observers about the strategy.
        """
        # print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)
        #We free the memory
        self.__strategy_report__.clear()
        self.__strategy_report__ = {}

    def update_report(self, time, position,
                    position_status, portfolio: pf.AbstractPortfolio, 
               verbose = False) -> None:
        """
        Update a report
        position: Long/Short
        position_status: Enter/Exit
        portfolio: portfolio linked to the strategy
        """
        self.__strategy_report__ [time]["Position"] = position
        self.__strategy_report__ [time]["Position Status"] = position_status
        self.__strategy_report__ [time]["Portfolio"] = portfolio.report()

    def report(self, verbose = False) -> dict:
        """
        Return a report of the strategy.
        it is a getter.
        """
        return self.__strategy_report__
    #########Observer Pattern#########
    ##################################


######################################
#We implement a command pattern to make the mediation
#Between strategy and portfolio
class StrategyCommandPortfolio(ABC):
    def __init__(self, portfolio: pf.AbstractPortfolio) -> None:
        #we command the portfolio from strategy
        self._portfolio = portfolio

    @property#=getPf=getter
    def portfolio(self) -> pf.Portfolio:
        '''
        Getter = Return the portfolio attached to the strategy
        '''
        return self._portfolio

    @portfolio.setter#=setPf
    def portfolio(self, portfolio: pf.Portfolio) -> None:
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
        if tmp_balance < 0:
            if self.portfolio.getState() != "STOPPED":
                self.portfolio.set_state(pfstate.PortfolioIsStopped())# PROBLEM
            print("No money in BAL = "+str(tmp_balance))
            return

        # tmp = 0.
        for key, quantity in list_investments.items(): #self.pf._children
            if not self.portfolio.is_key_exists(key):
                new_share = pf.Share(key, quantity)#(key, quantity, time)
                self.portfolio.add_share(new_share)
            else:
                # child.addShareQuantity(time, quantity) and add to a dict
                share = self.portfolio.get_share(key)
                share.add_share_quantity(quantity)
                #the long (+) are substracted
                #the short (-) are added to the BAL
                tmp_balance -= (self.portfolio.get_share(key).value(time))
            # if quantity < 0:
            #     tmp_balance += (self.pf.get_share(key).value(time))
            # else :
            #     tmp_balance -= (self.pf.get_share(key).value(time))

        # tmp_balance = self._portfolio.get_BAL() - tmp_balance
        self.portfolio.set_BAL(tmp_balance)
        self.portfolio.update_portfolio(time)
        self.portfolio.notify()#each time we notify we send the pf

    def exit(self, time: datetime, verbose = False) -> None:
        """
        Here, when we exit, we release every shares.
        """
        if verbose:
            print("We exit the strat.")

        # tmp_balance = 0
        tmp_portfolio_value = self.portfolio.value(time)
        shares = self.portfolio.get_shares()
        for key in shares.keys():
            # We release every shares
            shares[key].set_share_quantity(0)

        #Then we update the portfolio
        self.portfolio.set_TCV (tmp_portfolio_value)
        self.portfolio.set_BAL (tmp_portfolio_value)
        # self.pf.update_portfolio(time)

        #ATTENTION CHECK IF IT IS GOOD
        self.portfolio.set_state(pfstate.PortfolioIsReady())
        self.portfolio.notify()#my state is now to position closed


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
