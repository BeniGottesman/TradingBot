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

    def quotation (self, close_open_time: str, _share_name: str, time: datetime)-> float:
        """
        Return the quotation of _share_name at time
        For this purpose the algorithm need to know
        close_open_time = 'Close Time' or 'Open Time'
        since the dataframe that encompass every quation has 2 indexes 
        i.e. Open/Close time
        """
        if close_open_time != 'Close Time' or\
        close_open_time != 'Open Time':
            close_open_time = "Close Time"

        tmp_df = self.__market_quotations__ [_share_name]
        tmp_df_closetime = tmp_df.index.get_level_values('Close Time')
        _quote_current_value = -123450.0
        #Enhance the loop 
        #see (2) about iloc
        if (tmp_df_closetime == time).any() : #greedy
            tmp_df = tmp_df.iloc[tmp_df_closetime == time] #greedy X2
            _quote_current_value = tmp_df["Close"].iloc[0]
        else:
            d = min(tmp_df_closetime, key=lambda _d: abs(_d - time))
            _quote_current_value = tmp_df[tmp_df_closetime==d]['Close'].iloc[0]

        return _quote_current_value

class MarketQuotationClient(metaclass=Singleton):
    def __init__(self, _quotations: pd.DataFrame):
        self.__client__ = MarketQuotation(_quotations)

    def get_client (self):
        return self.__client__

#References
#(2) https://stackoverflow.com/questions/16729574/how-can-i-get-a-value-from-a-cell-of-a-dataframe
