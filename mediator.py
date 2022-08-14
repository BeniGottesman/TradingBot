from abc import ABC, abstractmethod
import random
import string
from sys import maxsize
# from typing import List
import Strategy.Strategy as st
import Portfolio.Portfolio as pf

#It is a mediator between Strat and portfolio
class mediator():

    @abstractmethod
    def execute(self, pf: pf.AbstractPortfolio, data: List):
        pass

class severalTrading(mediator):

    def __init__(self, portfolio: pf.AbstractPortfolio) -> None:
        #we command the portfolio from strategy
        self.__strategy__: dict[Trading] = {}

    def load (self, strategy:st.Strategy, portfolio: pf.AbstractPortfolio) -> None:
        tmp = Trading(strategy, portfolio)
        key = tmp.getID()
        self.__strategy__[key] = tmp

    def unload (self, stratID: int) -> None:
        if self.__strategy__.has_key(stratID):
            del self.__strategy__ [stratID]

    def execute(self, pf: pf.AbstractPortfolio, data: List):
        i = 0
        for i in len(self.__mediators__):
            self.__mediators__.execute()

class Trading (mediator):

    def __init__(self, strategy:st.Strategy, portfolio: pf.AbstractPortfolio) -> None:
        #we command the portfolio from strategy
        self.__strategy__  = strategy
        self.__portfolio__ = portfolio
        self.__name__ = random.randint(1, maxsize) #unique
        portfolio.setID(self.__name__)

    def getID(self) -> int:
        return self.__name__

    def execute(self, pf: pf.AbstractPortfolio, data: List):
        return