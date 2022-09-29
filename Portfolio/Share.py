from __future__ import annotations
# from abc import abstractmethod
import string
from typing import List
import datetime
import numpy as np
#import Portfolio.PfState as st
import designPattern.state as st
import Portfolio.abstract_instrument as ai
import market_quotation as mq


# Leaf
# Share = crypto, fx, call, put etc
class Share(ai.AbstractInstrument):
    _state = None

    def __init__(self, _type, _name) -> None:
        super().__init__(_type, _name)
        # self.__name__ = _name #for instance BTCUSDT
        self.__time_now__ = 0
        self.__state__ = st.NothingState()#Make ShareState class
        self.__number_of_shares__ = 0
        # self.__BaseCurrentValue__ = 1 because 1 BTC = X Dollar
        # self.__quoteCurrentValue__ = 0 #for 1 BTC = QuoteCurrentValue $

    def set_state(self, state: st.State) -> None:
        self.__state__ = state

    def get_share_quantity (self):
        return self.__number_of_shares__
    def set_share_quantity (self, quantity: float):
        self.__number_of_shares__ = quantity
    def add_share_quantity(self, share_quantity: float) -> None:
        self.__number_of_shares__ += share_quantity

    def report(self) -> dict:
        return {self.__number_of_shares__, self.value()}

    # @abstractmethod
    # def updateQuotation (self, listQuotations, verbose = False) -> None:
    #     pass
    # @abstractmethod
    # def isKeyExists (key: string) -> bool:
    #     pass

class CryptoCurrency(Share):
    def __init__(self, _name) -> None:
        _type="cryptoCurrency"
        super().__init__(_type, _name)

    #deprecated
    #market value
    def get_quote_current_value (self):
        return self.value()/self.__number_of_shares__
    #Deprecated
    # def updateMarketQuotation (self,  time: datetime, value: float, verbose = False) -> None:
    #     self.__quoteCurrentValue__ = value

    def get_pair(self)-> str:
        return self.__name__

    #return the value hold in $
    #ToUpdate
    def value(self, time: datetime=datetime.date(1970, 1, 1)) -> str:
        market_quotation = mq.MarketQuotationClient().get_client()
        _share_name = self.__name__
        _quote_current_value = market_quotation.quotation('Close Time', _share_name, time)
        return _quote_current_value * self.__number_of_shares__

    def is_key_exists (self, key: string) -> bool:
        if key != self.__name__:
            return False
        return True


# References
# https://refactoring.guru/fr/design-patterns/composite/python/example
#(2) https://stackoverflow.com/questions/16729574/how-can-i-get-a-value-from-a-cell-of-a-dataframe
