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

    def number_of_period(self)-> int:
        """
        return the number of quotation in the historic
        """
        sym = list(self.__market_quotations__.keys())[0]
        return len(self.__market_quotations__[sym])

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
            _date = min(tmp_df_closetime, key=lambda _d: abs(_d - time))
            _quote_current_value = tmp_df[tmp_df_closetime==_date]['Close'].iloc[0]

        return _quote_current_value

    def time (self, _share_name: str, _close_or_open_time: str, _time_index:int):
        tmp_df = self.__market_quotations__ [_share_name]
        if _close_or_open_time == "Open Time":
            return tmp_df[0:_time_index].index.get_level_values(_close_or_open_time)[-1]
        return tmp_df[0:_time_index].index.get_level_values('Close Time')[-1]

    def get_index (self, _share_name: str, _close_or_open_time: str, beginning: int, end: int):
        """
        Return the index of a given share between
        beginning and end.
        """
        tmp_df = self.__market_quotations__ [_share_name]
        if _close_or_open_time == "Open Time":
            return tmp_df [ beginning : end ]\
                        .index.get_level_values('Open Time')
        return tmp_df [ beginning : end ].index.get_level_values('Close Time')

class MarketQuotationClient(metaclass=Singleton):
    def __init__(self, _quotations: pd.DataFrame):
        self.__client__ = MarketQuotation(_quotations)

    def get_client (self):
        return self.__client__

#References
#(2) https://stackoverflow.com/questions/16729574/how-can-i-get-a-value-from-a-cell-of-a-dataframe
# Binance Fees calculator : https://www.binance.com/en/support/faq/e85d6e703b874674840122196b89780a
#(1) https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pandas-dataframe
#(3) https://stackoverflow.com/questions/18835077/selecting-from-multi-index-pandas
