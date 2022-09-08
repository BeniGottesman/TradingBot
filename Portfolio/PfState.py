from abc import abstractmethod
import datetime
import designPattern.state as st
import Portfolio.Portfolio as pf

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class PortfolioState(st.state):
    def __init__(self, _state, _time: datetime, _value: float) -> None:
        super().__init__(_time, _value)
        self.__state__ = _state
        
    @abstractmethod
    def __str__(self): 
        pass
    
    @abstractmethod
    def myStateIs (self) -> None:
        pass
    
    @abstractmethod
    def getState (self) -> str:
        pass
    
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, PortfolioState):
            return self.__state__ == other.__state__
        return False
    
class PortfolioIsReady (PortfolioState):
    def __init__(self, _time: datetime, _value: float) -> None:
        super().__init__("READY", _time, _value)
    
    def __str__(self): 
        return "READY"

    def myStateIs (self) -> None:
        print ("Ready")
    
    def getState (self) -> str:
        return "READY"
    


class NoMoneyInBAL (PortfolioState):
    def __init__(self, _time: datetime, _value: float) -> None:
        super().__init__("No Money in BAL", _time, _value)
        
    def __str__(self): 
        return "No Money in BAL"

    def myStateIs (self) -> None:
        print ("No Money in BAL")
    
    def getState (self) -> str:
        return "No Money in BAL"

class PortfolioIsStopped (PortfolioState):
    def __init__(self, _time: datetime, _value: float) -> None:
        super().__init__("STOPPED", _time, _value)
        
    def __str__(self): 
        return "STOPPED"

    def myStateIs (self) -> None:
        print ("Stopped")
    
    def getState (self) -> str:
        return "STOPPED"