from abc import abstractmethod
from datetime import datetime
import Strategy.strategy as strat
import designPattern.state as st
# import Portfolio.Portfolio as pf

    # The common state interface for all the states
    # Context = Portfolio, Share etc
    # https://auth0.com/blog/state-pattern-in-python/
class StrategyState(st.StateAbstract):
    #__savePfState__=
    # Contain the value of the pf when we enter the strat->useful for computing a stop loss
    def __init__(self, time: datetime, strategy: strat.Strategy):
        super().__init__()
        self.__strategy__   = strategy
        # Time at which we entered the strategy.
        self.__entry_time__ = time

    @abstractmethod
    def get_state (self) -> str:
        return self

    def state_of_strategy (self) -> str:
        """
        Return a string containing the state.
        """
        pass

    @abstractmethod
    def __eq__(self, str_other: str):
        if self.state_of_strategy() == str_other:
            return True
        return False

    @abstractmethod
    def my_state_is (self) -> None:
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def freeze (self,  time:datetime, _time_cycle: int) -> None :
        pass

    @abstractmethod
    def trailing_buy(self, time_now:datetime, investment_dict, transaction_cost) -> None :
        pass
    @abstractmethod
    def trailing_sell(self, time:datetime, transaction_cost: float) -> None :
        pass
    @abstractmethod
    def trailing_stop(self, time:datetime) -> None :
        pass
    @abstractmethod
    def rebalance(self, time:datetime) -> None : #hedging
        pass

    __short_strategy__ = False
    def is_strategy_short (self) -> bool :
        return self.__short_strategy__
    def set_strategy_short (self, _b: bool):
        self.__short_strategy__ = _b

    def elapsed_time (self, _time: datetime) -> float:
        """
        Return the time elapsed between the moment
        we entered the strategy/state and _time in second.
        """
        _c = _time - self.__entry_time__
        return _c.total_seconds()

class StrategyWaitToEntry (StrategyState): #== Strategy is Ready
    def __str__(self):
        return "waitToEntry"

    def my_state_is (self) -> None:
        print ("Strategy : Wait for an entry Signal")

    def state_of_strategy (self) -> str:
        return "WaitToEntry"

    def freeze (self, time:datetime, _time_cycle: int) -> None :
        self.__strategy__.change_state(StrategyFreeze(self, time, _time_cycle))

    def trailing_buy(self, time_now, investment_dict, transaction_cost) -> None :
        self.__strategy__ .entry(time_now, investment_dict, transaction_cost)
        return
    def trailing_sell(self, time:datetime, transaction_cost: float) -> None :
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

    def state_of_strategy (self) -> str:
        return "WaitToExit"

    def freeze (self, time:datetime, _time_cycle: int) -> None :
        self.__strategy__.change_state(StrategyFreeze(self, time, _time_cycle))

    def trailing_buy(self, time_now:datetime, investment_dict, transaction_cost) -> None :
        return
    def trailing_sell(self, time: datetime, transaction_cost: float) -> None :
        self.__strategy__.exit(time, transaction_cost)
    def trailing_stop(self, time:datetime) -> None :
        return
    def rebalance(self, time:datetime) -> None : #hedging
        return

class StrategyFreeze (StrategyState):
    def __init__(self, time_now: datetime, strategy: strat.Strategy, _freeze_time_: int):
        super().__init__(time_now, strategy)
        self.__freeze_time__ = _freeze_time_
        self.__cycle_counter__ = 0

    def __str__(self):
        return "Freeze"

    def my_state_is (self) -> None:
        cycle = self.__cycle_counter__
        print ("Strategy : has been Frozen for ",cycle," cycle")

    def state_of_strategy (self) -> str:
        return "Freeze"

    def get_counter(self) -> int:
        return self.__cycle_counter__

    def add_counter(self, time_now: datetime) -> None:
        strategy = self.__strategy__
        if self.__cycle_counter__ < self.__freeze_time__:
            self.__cycle_counter__ = self.__cycle_counter__ + 1
            if self.__cycle_counter__ >= self.__freeze_time__:
                strategy.change_state (StrategyWaitToEntry(time_now, strategy))

    def freeze (self, time:datetime, _time_cycle: int) -> None :
        return

    def trailing_buy(self, time_now:datetime, investment_dict, transaction_cost) -> None :
        return
    def trailing_sell(self, time:datetime, transaction_cost: float) -> None :
        return
    def trailing_stop(self, time:datetime) -> None :
        return
    def rebalance(self, time:datetime) -> None : #hedging
        return

    def is_strategy_short (self) -> bool :
        self.short_strategy = False
        return self.short_strategy
