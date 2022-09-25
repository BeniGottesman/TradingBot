from datetime import datetime
import pandas as pd
from designPattern.singleton import Singleton

class MarketQuotation():
    def __init__(self, _quotations: pd.DataFrame):#, _quotations: pd.DataFrame):
        self.__market_quotations__ = _quotations

    def set_quotations (self, _quotations: pd.DataFrame)-> None:
        self.__market_quotations__ = _quotations

    def get_quotation (self)-> dict:
        return self.__market_quotations__

    def insert (self, currency: str, time: datetime, value: float)-> None:
        self.__market_quotations__[currency][time] = value

class MarketQuotationClient(metaclass=Singleton):
    def __init__(self, _quotations: pd.DataFrame):
        self.__client__ = MarketQuotation(_quotations)

    def get_client (self):
        return self.__client__
    