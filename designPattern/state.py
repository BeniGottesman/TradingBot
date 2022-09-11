from abc import abstractmethod
from operator import truediv
# import datetime


class StateAbstract():
    # def __init__(self):
    #     self.__savePfState__ = _value
        # self.__savePfTime__  = _time

    @abstractmethod
    def my_state_is (self) -> None:
        pass

    @abstractmethod
    def get_state (self) -> str:
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    # def get_value (self) -> float:
    #     return self.__savePfState__


class NothingState(StateAbstract):
    # def __init__(self):
    #     super().__init__()

    def __str__(self):
        return "nothing"

    def my_state_is (self) -> None:
        print ("...")

    def get_state (self) -> str:
        return "nothing"

    #Check again : Useless ?
    def __eq__(self, other):
        if isinstance(other, NothingState):
            return True
        return False

# References
# The common state interface for all the states
# Context = Portfolio, Share etc
#https://auth0.com/blog/state-pattern-in-python/
