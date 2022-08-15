from abc import abstractmethod

# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
class state():

    @abstractmethod
    def myStateIs (self) -> None:
        pass

    @abstractmethod
    def getState (self) -> None:
        pass

    @abstractmethod
    def __str__(self): 
        pass

class nothingState(state):

    def __str__(self): 
        return "nothing"

    def myStateIs (self) -> None:
        print ("...")