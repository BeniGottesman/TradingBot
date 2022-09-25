from abc import abstractmethod
# import datetime
import designPattern.state as st
import Portfolio.portfolio as pf

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class PortfolioState(st.StateAbstract):
    def __init__(self, _state) -> None:
        super().__init__()
        self.__state__ = _state

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def my_state_is (self) -> None:
        pass

    @abstractmethod
    def get_state (self) -> str:
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

    def my_state_is (self) -> None:
        print ("Ready")

    def get_state (self) -> str:
        return "READY"



class NoMoneyInBAL (PortfolioState):
    def __init__(self) -> None:
        super().__init__("No Money in BAL")

    def __str__(self): 
        return "No Money in BAL"

    def my_state_is (self) -> None:
        print ("No Money in BAL")

    def get_state (self) -> str:
        return "No Money in BAL"

class PortfolioIsStopped (PortfolioState):
    def __init__(self) -> None:
        super().__init__("STOPPED")

    def __str__(self):
        return "STOPPED"

    def my_state_is (self) -> None:
        print ("Stopped")

    def get_state (self) -> str:
        return "STOPPED"
    