from abc import ABC, abstractmethod
import random
import string
from sys import maxsize
from typing import List
import Strategy.Strategy as st
import Portfolio.Portfolio as pf

class mediator():

    @abstractmethod
    def execute(self, pf: pf.AbstractPortfolio, data: List):
        pass

class severalMediator(mediator):

    def __init__(self, portfolio: pf.AbstractPortfolio) -> None:
        #we command the portfolio from strategy
        self.__strategy__: dict[strat] = {}

    def add (self, strategy:st.Strategy, portfolio: pf.AbstractPortfolio) -> None:
        tmp = strat(strategy, portfolio)
        key = tmp.getID()
        self.__strategy__[key] = tmp

    def remove (self, stratID: int) -> None:
        delThis = self.__strategy__[stratID]
        self.__strategy__.remove (delThis) 

    def execute(self, pf: pf.AbstractPortfolio, data: List):
        i = 0
        for i in len(self.__mediators__):
            self.__mediators__.execute()

class strat(mediator):

    def __init__(self, strategy:st.Strategy, portfolio: pf.AbstractPortfolio) -> None:
        #we command the portfolio from strategy
        self.__strategy__  = strategy
        self.__portfolio__ = portfolio
        self.__name__ = random.randint(0, maxsize)

    def getID(self) -> int:
        return self.__name__

    def execute(self, pf: pf.AbstractPortfolio, data: List):
        return