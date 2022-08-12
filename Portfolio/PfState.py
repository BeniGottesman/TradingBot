from abc import abstractmethod
import Portfolio.Portfolio as pf

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class PortfolioState():

    @abstractmethod
    def myStateIs (self) -> None:
        pass

    @abstractmethod
    def __str__(self): 
        pass

class PortfolioIsReady (PortfolioState):
    def __str__(self): 
        return "READY"

    def myStateIs (self) -> None:
        print ("Ready")

class NoMoneyInBAL (PortfolioState):
    def __str__(self): 
        return "No Money in BAL"

    def myStateIs (self) -> None:
        print ("No Money in BAL")

class PortfolioIsStopped (PortfolioState):
    def __str__(self): 
        return "STOPPED"

    def myStateIs (self) -> None:
        print ("Stopped")