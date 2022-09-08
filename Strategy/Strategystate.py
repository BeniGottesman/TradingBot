from abc import abstractmethod
from datetime import datetime
import designPattern.state as st
# import Portfolio.Portfolio as pf

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class StrategyState(st.state):
             #__savePfState__=Contain the value of the pf when we enter the strat -> useful for computing a stop loss
    def __init__(self, _time: datetime, _value: float):
        super().__init__(_time, _value)
        
    @abstractmethod
    def myStateIs (self) -> None:
        pass

    @abstractmethod
    def __str__(self): 
        pass

class StrategyWaitToEntry (StrategyState):
    def __str__(self): 
        return "waitToEntry"

    def myStateIs (self) -> None:
        print ("Strategy : Wait for an entry Signal")

    def getState (self) -> None:
        return "WaitToEntry"

class StrategyWaitToExit (StrategyState):
    def __str__(self): 
        return "WaitToExit"

    def myStateIs (self) -> None:
        print ("Strategy : Wait for an exit Signal")
    
    def getState (self) -> None:
        return "WaitToExit"