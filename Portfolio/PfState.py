from abc import abstractmethod
import designPattern.state as st
import Portfolio.Portfolio as pf

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class PortfolioState(st.state):
    def __init__(self, _state) -> None:
        self.__state__ = _state
        
    @abstractmethod
    def __str__(self): 
        pass
    
    @abstractmethod
    def myStateIs (self) -> None:
        pass
    
    @abstractmethod
    def getState (self) -> None:
        pass
    
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, PortfolioState):
            return self.__state__ == other.__state__
        return False
    
class PortfolioIsReady (PortfolioState):
    def __init__(self) -> None:
        super().__init__("READY")
    
    def __str__(self): 
        return "READY"

    def myStateIs (self) -> None:
        print ("Ready")
    
    def getState (self) -> None:
        return "READY"
    


class NoMoneyInBAL (PortfolioState):
    def __init__(self) -> None:
        super().__init__("No Money in BAL")
        
    def __str__(self): 
        return "No Money in BAL"

    def myStateIs (self) -> None:
        print ("No Money in BAL")
    
    def getState (self) -> None:
        return "No Money in BAL"

class PortfolioIsStopped (PortfolioState):
    def __init__(self) -> None:
        super().__init__("STOPPED")
        
    def __str__(self): 
        return "STOPPED"

    def myStateIs (self) -> None:
        print ("Stopped")
    
    def getState (self) -> None:
        return "STOPPED"