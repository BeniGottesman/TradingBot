from __future__ import annotations
from abc import ABC, abstractmethod
import datetime
from tkinter.messagebox import NO
from typing import List

import Strategy.command as btcmd
import Portfolio.portfolio as pf
import Portfolio.portfolio_state as pfstate
import Strategy.strategy_state as strategy_state
import designPattern.observer as obs
import Strategy.statistics as stat

class Strategy(obs.Subject):
    def __init__(self, portfolio: pf.Portfolio, _freezing_cycle: int,
                _initial_investment_percentage: float, stop_loss_activated: bool):
        self.__strategy_report__ = {}
        self.__backtest_command__ = btcmd.BacktestCommand(portfolio)
        self._state = strategy_state.StrategyWaitToEntry()
        self._short_strategy = False
        #How many cycle do I freeze the strategy ?
        self._freezing_cycle = _freezing_cycle
        #initial_investment_percentage=This variable is 1 i.e. not used yet
        #i.e. 0.2% of the capital for instance
        self._initial_investment_percentage = _initial_investment_percentage
        self._stop_loss_activated = stop_loss_activated
        #Observers
        self._statistics_viewer = stat.StatisticsViewer()
        self.attach (self._statistics_viewer)#don't forget to remove it at the end

    @abstractmethod
    def do_strategy(self, constant_std: float, data: List, verbose = False):
        """
        Start the strategy.
        """
        pass

    ###############################
    #########State Pattern#########
    def change_state (self, _state: strategy_state) -> None :
        self._state = _state
    def get_state (self)-> str :
        return self._state.get_state()

    def freeze (self) -> None :
        self._state.freeze (self, )
    #########State Pattern#########
    ###############################

    def get_portfolio(self) -> pf.Portfolio:
        return self.__backtest_command__.get_portfolio()

    ##################################
    #########Observer Pattern#########
    __observers__: List[obs.Observer] = []

    def attach(self, observer: obs.Observer) -> None:
        # print("Strategy: Attached an observer to strategy.")
        self.__observers__.append(observer)

    def detach(self, observer: obs.Observer) -> None:
        self.__observers__.remove(observer)

    def notify(self, verbose = False) -> None:
        """
        Notify/Send a report to all observers about the strategy.
        """
        # print("Subject: Notifying observers...")
        for observer in self.__observers__:
            observer.update(self)
        #We free the memory
        self.__strategy_report__.clear()
        self.__strategy_report__ = {}

    def update_report(self, _time: datetime, position,
                        position_status, portfolio: pf.AbstractPortfolio,
                        verbose = False) -> None:
        """
        Update a report
        position: Long/Short
        position_status: Enter/Exit
        portfolio: portfolio linked to the strategy
        """
        self.__strategy_report__ [_time] = {}
        self.__strategy_report__ [_time]["Position"] = position
        self.__strategy_report__ [_time]["Position Status"] = position_status
        #Just keep once the TCV -> scale graph
        self.__strategy_report__ [_time]["Portfolio"] = portfolio.get_report(_time)

    def get_report(self, _time: datetime=datetime.date(1970, 1, 1), verbose = False) -> dict:
        """
        Return a report of the strategy.
        it is a getter.
        """
        return self.__strategy_report__
    #########Observer Pattern#########
    ##################################

    #################################
    #########Command Pattern#########
    @abstractmethod
    def entry(self, time: datetime, list_investments: dict, verbose = False) -> None:
        self.__backtest_command__.entry (time, list_investments)

    @abstractmethod
    def exit(self, time: datetime, verbose = False) -> None:
        self.__backtest_command__.exit (time)
    #########Command Pattern#########
    #################################
