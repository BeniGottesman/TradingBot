from abc import abstractmethod
from datetime import datetime
import strategy as strat
import designPattern.state as st
# import Portfolio.Portfolio as pf

    # The common state interface for all the states
    # Context = Portfolio, Share etc
    # https://auth0.com/blog/state-pattern-in-python/
class StrategyState(st.StateAbstract):
    #__savePfState__=
    # Contain the value of the pf when we enter the strat->useful for computing a stop loss
    def __init__(self, strategy: strat.Strategy):
        super().__init__()
        self.__strategy__ = strategy

    @abstractmethod
    def get_state (self) -> str:
        """
        Return a string containing the state.
        """
        pass

    @abstractmethod
    def my_state_is (self) -> None:
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def freeze (self, _time_cycle: int) -> None :
        pass

    @abstractmethod
    def trailing_buy(self, time_now:datetime, investment_dict) -> None :
        pass
    @abstractmethod
    def trailing_sell(self, time:datetime) -> None :
        pass
    @abstractmethod
    def trailing_stop(self, time:datetime) -> None :
        pass
    @abstractmethod
    def rebalance(self, time:datetime) -> None : #hedging
        pass


class StrategyWaitToEntry (StrategyState): #== Strategy is Ready
    def __str__(self):
        return "waitToEntry"

    def my_state_is (self) -> None:
        print ("Strategy : Wait for an entry Signal")

    def get_state (self) -> str:
        return "WaitToEntry"

    def freeze (self, _time_cycle: int) -> None :
        self.__strategy__.change_state(StrategyFreeze(_time_cycle))

    def trailing_buy(self, time_now, investment_dict) -> None :
        self.__strategy__ .entry(time_now, investment_dict)
        return
    def trailing_sell(self, time:datetime) -> None :
        return
    def trailing_stop(self, time:datetime) -> None :
        return
    def rebalance(self, time:datetime) -> None : #hedging
        return

class StrategyWaitToExit (StrategyState):
    def __str__(self):
        return "WaitToExit"

    def my_state_is (self) -> None:
        print ("Strategy : Wait for an exit Signal")

    def get_state (self) -> str:
        return "WaitToExit"

    def freeze (self, _time_cycle: int) -> None :
        self.__strategy__.change_state(StrategyFreeze(_time_cycle))

    def trailing_buy(self, time_now:datetime, investment_dict) -> None :
        return
    def trailing_sell(self, time: datetime) -> None :
        self.__strategy__.exit(time)
    def trailing_stop(self, time:datetime) -> None :
        return
    def rebalance(self, time:datetime) -> None : #hedging
        return

class StrategyFreeze (StrategyState):
    def __init__(self, _freeze_time_: int):
        self.__freeze_time__ = _freeze_time_
        self.__cycle_counter__ = 0

    def __str__(self):
        return "Freeze"

    def my_state_is (self) -> None:
        cycle = self.__cycle_counter__
        print ("Strategy : has been Frozen for ",cycle," cycle")

    def get_state (self) -> str:
        return "Freeze"

    def get_counter(self) -> int:
        return self.__cycle_counter__

    def add_counter(self) -> None:
        strategy = self.__strategy__
        if self.__cycle_counter__ < self.__freeze_time__:
            self.__cycle_counter__ = self.__cycle_counter__ + 1
            if self.__cycle_counter__ >= self.__freeze_time__:
                strategy.change_state (StrategyWaitToEntry(strategy))

    def freeze (self, _time_cycle: int) -> None :
        return

    def trailing_buy(self, time_now:datetime, investment_dict) -> None :
        return
    def trailing_sell(self, time:datetime) -> None :
        return
    def trailing_stop(self, time:datetime) -> None :
        return
    def rebalance(self, time:datetime) -> None : #hedging
        return
