"""Portfolio.py"""

# https://refactoring.guru/fr/design-patterns/composite/python/example

from __future__ import annotations
from abc import abstractmethod
import string
from typing import List
import numpy as np
# from datetime import datetime
import designPattern.observer as obs
import designPattern.Memento as Memento
import Portfolio.PfState as state
import Portfolio.Share as share
import Portfolio.AbstractInstrument as ai

class AbstractPortfolio(ai.AbstractInstrument, obs.Subject):

    #code duplication
    # def __init__(self, _type="currency", _name="generic portfolio") -> None:
    #     super().__init__(_type, _name)

    def add(self, portfolio: AbstractPortfolio) -> None:
        pass

    def remove(self, portfolio: AbstractPortfolio) -> None:
        pass

    def is_composite(self) -> bool:
        return False

    ##################################
    #########Observer Pattern#########
    # _state: int = None
    __observers__: List[obs.Observer] = []

    def attach(self, observer: obs.Observer) -> None:
        print("Subject: Attached an observer.")
        self.__observers__.append(observer)

    def detach(self, observer: obs.Observer) -> None:
        self.__observers__.remove(observer)


    @abstractmethod
    def getWeightArrayOfShares (self) -> np.array:
        pass

    @abstractmethod
    def notify(self, verbose = False) -> None:        
        pass
    @abstractmethod
    def report(self, verbose = False) -> dict:       
        pass
    #########Observer Pattern#########
    ##################################

    #######################
    ####Memento Pattern####
    @abstractmethod
    def generateStateData(self) -> dict:
        pass

    def save(self) -> Memento:
        """
        Saves the current state inside a memento.
        """
        my_portfolio_state = self.generateStateData()
        return Memento.ConcreteMemento(my_portfolio_state)


    @abstractmethod
    def restoreState(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
    ####Memento Pattern####
    #######################

#https://wiki.profittrailer.com/en/webinterfaceguide
class severalPortfolios(AbstractPortfolio):
    def __init__(self, _type="currency?", _name="generic Bunch of portfolio") -> None:
        super().__init__(_type, _name)
        self.__portfolios__: List[AbstractPortfolio] = []
        #TCV=Total Current Value
        self.__TCV__ = 0
        #BAL = Balance
        self.__BAL__ = 0

    def add(self, portfolio: AbstractPortfolio) -> None:
        self.__portfolios__.append(portfolio)
        self.__TCV__ = self.get_TCV()
        portfolio.parent = self

    def remove(self, portfolio: AbstractPortfolio) -> None:
        self.__TCV__ -= self.get_TCV()
        self.__portfolios__.remove(portfolio)
        portfolio.parent = None

    #######################
    ####Memento Pattern####
    def generateStateData(self) -> dict:
        state_portfolios = {}
        my_portfolios = self.__portfolios__
        for portfolio in my_portfolios:
            state_portfolios [portfolio.get_name()] = portfolio.generateStateData(portfolio)
        return state_portfolios

    def restoreState(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
        my_portfolios_state = memento.get_state()#retutrn a dictionary
        my_portfolios       = self.__portfolios__
        #it is a list it is preferable to browse/loop it with an index i=0..n
        for portfolio in my_portfolios:
            key = portfolio.get_name()
            portfolio.restoreState(my_portfolios_state[key])
    ####Memento Pattern####
    #######################

    #########################
    ####TCV getter setter####
    def get_TCV(self) -> float:
        tmp_TCV = 0
        for portfolio in self.__portfolios__:
            tmp_TCV += portfolio.get_TCV()
        return tmp_TCV
    ### WARNING WHEN USE IT
    def set_TCV(self, value: float) -> None:
        if value > self.get_TCV():
            self.__TCV__ = value
    def add_TCV(self, value: float) -> None:
        self.__TCV__ += value
    ### WARNING WHEN USE IT
    
    ####TCV getter setter####
    #########################

    def getWeightArrayOfShares (self) -> np.array:
        tmp_array = [] #np.array()
        for portfolio in self.__portfolios__:
             tmp_array = np.append(tmp_array, portfolio.getWeightArrayOfShares())
        return tmp_array

    #########################
    ####BAL getter setter####
    def get_BAL(self) -> float:
        tmp_BAL = 0
        for portfolio in self.__portfolios__:
            tmp_BAL += portfolio.get_BAL()
        return tmp_BAL
    # WARNING WHEN USE IT
    #LA TCV EVOLUE INDEPENDEMMENT DE LA BAL
    def set_BAL(self, value: float) -> None:
        if value > self.get_TCV():#SAUF CAS PARTICULIER OU BAL>TCV ...
            self.__BAL__ = value
        self.__BAL__ = value
    def add_BAL(self, value: float) -> None:
        self.__BAL__ += value
        tmp_TCV = self.get_TCV()
        self.__BAL__ = min(self.__BAL__, tmp_TCV)
    # WARNING WHEN USE IT
    ####BAL getter setter####
    #########################

    def is_composite (self) -> bool:
        return True

    def notify(self, verbose = False) -> None:
        if verbose:
            print("Subject: Notifying observers...")
        for observer in self.__observers__:
            observer.update(self)

####DEPRECATED
    # def updateMarketQuotation (self,  time: datetime, listQuotations, verbose = False) -> None:
    #     portfolios = self.__portfolios__
    #     self.__timeNow__ = time
    #     for i in len(portfolios):
    #         portfolios[i].updateMarketQuotation(self, time, listQuotations)
####DEPRECATED

    def is_key_exists (self, key: string) -> bool:
        portfolios = self.__portfolios__
        pf_numbers = len(portfolios)
        for i in range(pf_numbers):
            portfolios[i].is_key_exists(key)

    def report(self, verbose = False) -> dict:
        portfolios = self.__portfolios__
        tmp_dict_pf = {}
        tmp_dict_pf["time"] = self.__timeNow__
        tmp_dict_pf["TCV"] = self.__BAL__
        tmp_dict_pf["BAL"] = self.__TCV__

        pf_numbers = len(portfolios)
        for i in range(pf_numbers):
            key = portfolios[i].get_name()
            tmp_dict_pf[key] = portfolios[i].report()
        return tmp_dict_pf

# leaf of share
#here we have a 1 period tree : 1 node + n leafs
class Portfolio(AbstractPortfolio):

    #quoteCurrency="USD(T)" usually
    def __init__(self,
                 quote_currency: string, portfolio_name: string, starting_money: float) -> None:
        super().__init__("Portfolio", portfolio_name)
        self.__time_last_transaction__ = 0 #represent the time when the last transaction Occur
        self.__shares__: dict[share.Share] = {}
        self.__number_of_shares__ = 0
        # self.__portfolioName__ = portfolioName
        self.__state__ = state.PortfolioIsReady()
        self.__quote_currency__ = quote_currency
        self.__BAL__ = abs(starting_money)
        self.__TCV__ = abs(starting_money)

#############################################################
##########################PF STATE###########################
    def set_state(self, _state: state.State) -> None:
        self.__state__ = _state

    def presentState(self) -> None: #toString
        state_name = self.__state__#string overload operator
        print(f"Portfolio is in {state_name}")

    def getState (self) -> str:
        return self.__state__.get_state()
##########################PF STATE###########################
#############################################################

#####################################
##########TCV getter setter##########
    def get_TCV(self) -> float: #REmettre a jours avec les donnees actuelles de marche
        my_shares = self.__shares__
        tmp = 0
        for key in my_shares.items():
            tmp += my_shares[key].value()
        self.__TCV__ = tmp
        return self.__TCV__

    def set_TCV(self, value: float) -> None:
        self.__TCV__ = value

    def add_TCV(self, value: float) -> None:
        self.__TCV__ += value
##########TCV getter setter##########
#####################################

####################################
#########BAL getter setter##########WARNING need to be private
    def get_BAL(self) -> float:
        return self.__BAL__
    def set_BAL(self, value: float) -> None:
        self.__BAL__ = value
    def add_BAL(self, value: float) -> None:
        self.__BAL__ += value
#########BAL getter setter##########
####################################

##############################################################
####################operator overloading######################
    # add two portfolios TCV
    def __add__(self, other) -> None:
        return self.get_TCV()+other.getTCV()

    def __str__(self):
        portfolio_content= "Portfolio = " + self.__name__
        portfolio_content+= ", Time = " + str (self.__time_last_transaction__)
        portfolio_content+= '\n'
        portfolio_content+= "Value of the portfolio = "+str(self.__TCV__)
        portfolio_content+= " "+self.__quote_currency__
        portfolio_content+= '\n'
        portfolio_content+= "BAL of the portfolio = "+str(self.__BAL__)+" "+self.__quote_currency__
        portfolio_content+= '\n'
        i=0
        my_shares = self.__shares__
        for key in my_shares.items():
            i+=1
            portfolio_content+= str(i)+". Share = "+key
            portfolio_content+= ", quantity = "+str(self.__shares__[key].getShareQuantity())
            portfolio_content+= '\n'
        return portfolio_content
####################operator overloading######################
##############################################################


#########################################################
####################MEMENTO PATTERN######################
#return a state of the portfolio
    def generateStateData(self) -> dict: #None:
        state_portfolios = {}
        state_portfolios ["Portfolio name"] = self.__name__
        state_portfolios ["Transaction Time"] = self.__time_last_transaction__
        state_portfolios ["TCV"] = self.__TCV__
        state_portfolios ["BAL"] = self.__BAL__
        my_shares = self.__shares__
        for key in my_shares.items():
            share_quantity = my_shares[key].getShareQuantity()
            state_portfolios [key] = share_quantity
        return state_portfolios

    def restoreState(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
        state_portfolios = memento.get_state()#retutrn a dictionary
        self.__name__ = state_portfolios ["Portfolio name"]
        self.__time_last_transaction__ = state_portfolios ["Transaction Time"]
        self.set_TCV(state_portfolios ["TCV"])
        self.set_BAL(state_portfolios ["BAL"])
        my_shares = self.__shares__
        for key in my_shares.items():
            share_quantity = state_portfolios [key]
            my_shares[key].setShareQuantity(share_quantity)

####################MEMENTO PATTERN######################
#########################################################

##############################################################
##########################About Shares########################
#No need to add setNumberOfShare ? We do not set we add()

    #return the number of shares I hold e.g. btc+eth+sol = 3
    def get_number_of_shares(self) -> int:
        return self.__number_of_shares__

    #get shares return a dict of shares
    def get_shares(self) -> dict[share.Share] :
        return self.__shares__

    #add share
    def add(self, _share: share.Share) -> None:
        key = _share.get_name()
        self.__shares__ [key] = _share
        _share.parent = self #?
        self.__number_of_shares__ += 1

    #remove share
    def remove(self, _share: share.Share) -> None:
        key = _share.get_name()
        self.__shares__.pop(key, None)
        _share.parent = None #?
        self.__number_of_shares__ -= 1

    def getWeightArrayOfShares (self) -> np.array:
        tmp_array = [] #np.array()
        my_shares = self.__shares__
        for key in my_shares.items():
            qty = my_shares[key].getShareQuantity()
            tmp_array = np.append(tmp_array, qty)
        return tmp_array

    def get_share (self, key: string) -> share.Share:
        if key in self.__shares__:
            return self.__shares__[key]
##########################About Shares########################
##############################################################

####################################
#########Composite Pattern##########
    def is_composite(self) -> bool:
        return False

    #Search by induction if a key exists
    def is_key_exists (self, key: string) -> bool:
        children = self.__shares__
        if key in children:
            return True #problem multiple true if by induction
        return False
#########Composite Pattern##########
####################################

####################################
######overload operator for []######
    def __getitem__(self, key):
        my_shares = self.__shares__
        if key in my_shares.items():
            return self.__shares__[key]
    def __setitem__(self, key, value):
        self.__shares__[key] = value
######overload operator for []######
####################################

    def get_portfolio_currency (self) -> string:
        return self.__quote_currency__

    #return the BAL, by induction,
    #it is preferable to updateValues before
    def value(self) -> float:
        tmp_value = 0
        my_shares = self.__shares__
        for key in my_shares.items():
            tmp_value += self.__shares__[key].value()
        return tmp_value

    #Update the quote value of the pairs
    #DEPRECATED
    #def updateMarketQuotation(self, time: datetime, listQuotations: dict, verbose = False) -> None:
    #     self.__timeLastTransaction__ = time
    #     children = self.__Shares__
    #     for key in listQuotations: #self.pf._children
    #         if key in children:
    #             children[key].updateMarketQuotation(time, listQuotations[key])

####################################
#########Observer Pattern###########
    def report(self, verbose = False) -> dict:
        children = self.__shares__
        tmp_dict = {}
        tmp_dict["TCV"] = self.__TCV__
        tmp_dict["BAL"] = self.__BAL__
        for key in children.items():
            tmp_dict[key] = children[key].report()
        return tmp_dict

    #test it
    def notify(self, verbose = False) -> None:        
        # tmpDict = self.report(self)
        for i in self.__observers__:
            self.__observers__[i].update(self)
#########Observer Pattern###########
####################################

#######################################
############MEMENTO PATTERN############
class PortfolioCaretaker():
    """
    The Caretaker doesn't depend on the Concrete Memento class. Therefore, it
    doesn't have access to the originator's state, stored inside the memento. It
    works with all mementos via the base Memento interface.
    """

    def __init__(self, portfolio: AbstractPortfolio) -> None:
        self._mementos = []
        self._originator = portfolio

    def backup(self) -> None:
        # print("\nCaretaker: Saving Originator's state...")
        self._mementos.append(self._originator.save())

    def undo(self) -> None:
        # if not len(self._mementos):
        if len(self._mementos) == 0:
            return

        memento = self._mementos.pop()
        # print(f"Caretaker: Restoring state to: {memento.get_name()}")
        try:
            self._originator.restoreState(memento)
        except Exception:
            self.undo()

    def show_history(self) -> None:
        # print("Caretaker: Here's the list of mementos:")
        for memento in self._mementos:
            print(memento.get_name())
############MEMENTO PATTERN############
#######################################

# if __name__ == "__main__":
#     tree = Portfolio()

#     branch1 = Portfolio()
#     branch1.add(Pair())
#     branch1.add(Pair())

#     branch2 = Portfolio()
#     branch2.add(Pair())

#     tree.add(branch1)
#     tree.add(branch2)
