"""Portfolio.py"""

# https://refactoring.guru/fr/design-patterns/composite/python/example

from __future__ import annotations
from abc import abstractmethod
import datetime
import string
from typing import List
import numpy as np
# from datetime import datetime
import designPattern.observer as obs
import designPattern.Memento as Memento
import Portfolio.PfState as state
import Portfolio.Share as share
import Portfolio.abstractinstrument as ai

class AbstractPortfolio(ai.AbstractInstrument, obs.Subject):

    #code duplication
    # def __init__(self, _type="currency", _name="generic portfolio") -> None:
    #     super().__init__(_type, _name)

    def add_share(self, portfolio: AbstractPortfolio) -> None:
        pass

    def remove_share(self, portfolio: AbstractPortfolio) -> None:
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
        """
        For observer pattern
        """
        pass
    @abstractmethod
    def report(self, verbose = False) -> dict:
        """
        Create q report and Notify the observators
        """
        pass
    #########Observer Pattern#########
    ##################################

    #######################
    ####Memento Pattern####
    @abstractmethod
    def generate_state_data(self) -> dict:
        pass

    def save(self, time: datetime=datetime.date(1970, 1, 1)) -> Memento:
        """
        Saves the current state inside a memento.
        """
        my_portfolio_state = self.generate_state_data()
        return Memento.ConcreteMemento(time, my_portfolio_state)


    @abstractmethod
    def restore_state(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
    ####Memento Pattern####
    #######################

    #################
    ####TCV & BAL####
    @abstractmethod
    def get_TCV(self) -> float:
        pass
    @abstractmethod
    def set_TCV(self, value: float) -> None:
        pass
    @abstractmethod
    def add_TCV(self, value: float) -> None:
        pass

    #BAL getter setter
    @abstractmethod
    def get_BAL(self) -> float:
        pass
    @abstractmethod
    def set_BAL(self, value: float) -> None:
        pass
    @abstractmethod
    def add_BAL(self, value: float) -> None:
        pass
    ####TCV & BAL####
    #################


#https://wiki.profittrailer.com/en/webinterfaceguide
class SeveralPortfolios(AbstractPortfolio):
    def __init__(self, _type="currency?", _name="generic Bunch of portfolio") -> None:
        super().__init__(_type, _name)
        self.__portfolios__: List[AbstractPortfolio] = []
        #TCV=Total Current Value
        self.__TCV__ = 0
        #BAL = Balance
        self.__BAL__ = 0

    def add_share(self, portfolio: AbstractPortfolio) -> None:
        self.__portfolios__.append(portfolio)
        self.__TCV__ = self.get_TCV()
        portfolio.parent = self

    def remove_share(self, portfolio: AbstractPortfolio) -> None:
        self.__TCV__ -= self.get_TCV()
        self.__portfolios__.remove(portfolio)
        portfolio.parent = None

    #######################
    ####Memento Pattern####
    def generate_state_data(self) -> dict:
        state_portfolios = {}
        my_portfolios = self.__portfolios__
        for portfolio in my_portfolios:
            state_portfolios [portfolio.get_name()] = portfolio.generate_state_data(portfolio)
        return state_portfolios

    def restore_state(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
        my_portfolios_state = memento.get_state()#retutrn a dictionary
        my_portfolios       = self.__portfolios__
        #it is a list it is preferable to browse/loop it with an index i=0..n
        for portfolio in my_portfolios:
            key = portfolio.get_name()
            portfolio.restore_state(my_portfolios_state[key])
    ####Memento Pattern####
    #######################

    ####################################
    ##########Portfolio Update##########
    def update_portfolio(self, time: datetime=datetime.date(1970, 1, 1))-> None:
        """
        Update the portfolio
        """
        for portfolio in self.__portfolios__:
            portfolio.update_portfolio(time)

    ##########Portfolio Update##########
    ####################################

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
    def get_TCV(self)-> float:
        """
        return the Total Current Value
        """
        return self.__TCV__

    #Warning you change it, without market quotation
    def set_TCV(self, value: float) -> None:
        self.__TCV__ = value

    #Warning - you change it, without market quotation or without BAL
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
    #Not working since get_TCV(TIME)
    def __add__(self, other) -> None:
        # return self.get_TCV()+other.getTCV()
        return self.__TCV__+other.__TCV__

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
        for key, this_share in my_shares.items():
            i+=1
            portfolio_content+= str(i)+". Share = "+key
            portfolio_content+= ", quantity = "+str(this_share.get_share_quantity())
            portfolio_content+= '\n'
        return portfolio_content
####################operator overloading######################
##############################################################


#########################################################
####################MEMENTO PATTERN######################
#return a state of the portfolio
    def generate_state_data(self) -> dict: #None:
        state_portfolios = {}
        state_portfolios ["Portfolio name"] = self.__name__
        state_portfolios ["Transaction Time"] = self.__time_last_transaction__
        state_portfolios ["TCV"] = self.__TCV__
        state_portfolios ["BAL"] = self.__BAL__
        my_shares = self.__shares__
        for key, this_share in my_shares.items():
            share_quantity = this_share.get_share_quantity()
            state_portfolios [key] = share_quantity
        return state_portfolios

    def restore_state(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
        state_portfolios = memento.get_state()#retutrn a dictionary
        self.__name__ = state_portfolios ["Portfolio name"]
        self.__time_last_transaction__ = state_portfolios ["Transaction Time"]
        self.set_TCV(state_portfolios ["TCV"])
        self.set_BAL(state_portfolios ["BAL"])
        my_shares = self.__shares__
        for key, this_share in my_shares.items():
            share_quantity = state_portfolios [key]
            this_share[key].setShareQuantity(share_quantity)

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
    def add_share(self, _share: share.Share) -> None:
        key = _share.get_name()
        if key in self.__shares__: #Rise an Exception
            return
        self.__shares__ [key] = _share
        _share.parent = self #?
        self.__number_of_shares__ += 1

    #remove share
    def remove_share(self, _share: share.Share) -> None:
        key = _share.get_name()
        self.__shares__.pop(key, None)
        _share.parent = None #?
        self.__number_of_shares__ -= 1

    def getWeightArrayOfShares (self) -> np.array:
        tmp_array = [] #np.array()
        my_shares = self.__shares__
        for _, this_share in my_shares.items():
            qty = this_share.getShareQuantity()
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
        for share_key, _ in my_shares.items():
            if key == share_key:#Test Validity
                return self.__shares__[key]
    def __setitem__(self, key, value):
        self.__shares__[key] = value
######overload operator for []######
####################################

    def get_portfolio_currency (self) -> string:
        return self.__quote_currency__

####################################
##########Portfolio Update##########
    def update_portfolio(self, time: datetime=datetime.date(1970, 1, 1))-> None:
        """
        Update the portfolio
        """
        tmp = self.value (time)
        #UPDATE Step
        self.__TCV__ = tmp
        # self.__BAL__ = tmp
##########Portfolio Update##########
####################################

    def value(self, time: datetime=datetime.date(1970, 1, 1)) -> float:
        """
        return the TCV, by induction,
        it is preferable to updateValues before
        """
        tmp_value = 0
        my_shares = self.__shares__
        for _, this_share in my_shares.items():
            tmp_value += this_share.value(time)
        return self.__BAL__ + tmp_value

    def set_transaction_time (self, time) -> None:
        self.__time_last_transaction__ = time

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
        for key, _ in children.items():
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

    def backup(self, time: datetime=datetime.date(1970, 1, 1)) -> None:
        # print("\nCaretaker: Saving Originator's state...")
        self._mementos.append(self._originator.save(time))

    def get_last_buying_value (self) -> float:
        last_value = self._mementos [-1]
        last_value = (last_value.get_state()) ["TCV"]
        return last_value

    def undo(self) -> None:
        # if not len(self._mementos):
        if len(self._mementos) == 0:
            return

        memento = self._mementos.pop()
        # print(f"Caretaker: Restoring state to: {memento.get_name()}")
        try:
            self._originator.restore_state(memento)
        except Exception:
            self.undo()

    def show_history(self) -> None:
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
