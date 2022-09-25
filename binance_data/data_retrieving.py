import os
import string
import sys
import pandas as pd
import numpy as np

fileDirectory = os.getcwd()
sys.path.append(fileDirectory+"binanceDataRetrieve\\")
from binance_data import download_kline as dk
import enums as cst


def retrieve_historic_from_binance_datas (parameters_scrap: dict):
    """
    Download the datas from binance.data, inside data folder
    and unzip them in csv
    """
    folder = parameters_scrap["folder"]
    years = parameters_scrap["years"]
    months = parameters_scrap["months"]
    symbols = parameters_scrap["symbols"]
    trading_type = parameters_scrap["trading_type"]
    intervals = parameters_scrap["intervals"]
    start_date = parameters_scrap["startDate"]
    end_date = parameters_scrap["endDate"]
    checksum = parameters_scrap["checksum"]
    for quote_currency in symbols: #quote currency
        num_symbols = len(symbols[quote_currency])
        dk.download_monthly_klines(trading_type, symbols[quote_currency],
                                   num_symbols, intervals, years, months,
                                   start_date, end_date, folder, checksum)
