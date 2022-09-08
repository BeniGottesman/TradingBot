from abc import abstractmethod
import datetime

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class state():
    def __init__(self, _time: datetime, _value: float):
        self.__savePfState__ = _value
        self.__savePfTime__  = _time

    @abstractmethod
    def myStateIs (self) -> None:
        pass

    @abstractmethod
    def getState (self) -> str:
        pass
    
    @abstractmethod
    def __str__(self): 
        pass
    
    @abstractmethod
    def __eq__(self, other):
        pass
    
    def getValue (self) -> float:
        return self.__savePfState__


class nothingState(state):
    def __init__(self, _time: datetime, _value: float):
        super().__init__(_time, _value)
        
    def __str__(self): 
        return "nothing"

    def myStateIs (self) -> None:
        print ("...")