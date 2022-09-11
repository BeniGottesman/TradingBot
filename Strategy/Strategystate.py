from abc import abstractmethod
from datetime import datetime
import designPattern.state as st
# import Portfolio.Portfolio as pf

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class StrategyState(st.StateAbstract):
    #__savePfState__=
    # Contain the value of the pf when we enter the strat->useful for computing a stop loss
    # def __init__(self):
    #     super().__init__()

    @abstractmethod
    def my_state_is (self) -> None:
        pass

    @abstractmethod
    def __str__(self):
        pass

class StrategyWaitToEntry (StrategyState):
    def __str__(self):
        return "waitToEntry"

    def my_state_is (self) -> None:
        print ("Strategy : Wait for an entry Signal")

    def get_state (self) -> None:
        return "WaitToEntry"

class StrategyWaitToExit (StrategyState):
    def __str__(self):
        return "WaitToExit"

    def my_state_is (self) -> None:
        print ("Strategy : Wait for an exit Signal")

    def get_state (self) -> None:
        return "WaitToExit"
    