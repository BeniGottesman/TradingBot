import os
import sys
import pandas as pd
import numpy as np

fileDirectory = os.getcwd()
sys.path.append(fileDirectory+"binanceDataRetrieve\\")
from binanceDataRetrieve import downloadkline as dk
import enums as cst


def retrieve_historic_from_binance_datas (parameters_scrap):
    """
    Download the datas from binance.data, inside data folder and
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

def csv_to_dataframe (file)->pd.DataFrame:
    """
    Convert a csv file into a DataFrame.
    """
    filepkl = file.split(".")[0]+".pkl" #pickle is for reading quickly the csv
    # if not os.path.exists(filepkl):
    hist_df = pd.read_csv(file)
    hist_df.columns = cst.HISTORICAL_BINANCE_COLUMN
    #As dates are returned from Binance as timestamps,
    #we first divide by 1000 and then set the units to seconds to convert correctly.
    hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit='s')
    hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']/1000, unit='s')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume',
                       'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
    #We convert our objects into numerical values using the to_numeric function.
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
    hist_df.to_pickle(filepkl)
    os.remove(file)

    return hist_df

#hist_df = CSVFolderToDataFrame("BNBUSDT", "spot", "15m")
def csv_pair_folder_to_dataframe (pair, trading_type, interval,verbose=False)->pd.DataFrame:
    """
    This Function Take A pair, trading type = ''spot'', and an interval=''15m''.
    Then convert the csv file into a dataframe.
    """
    relative_path = "data\\"+trading_type+"\\monthly\\klines\\"+pair+"\\"+interval+"\\"

    #We now merge
    frames = []
    for file in os.listdir(relative_path):
        if file.endswith(".csv"):
            if verbose:
                print ("merge = ", file)
            frames.append (csv_to_dataframe(relative_path+file))
        elif file.endswith(".pkl"):
            frames.append (pd.read_pickle(relative_path+file))
    hist_df = pd.concat(frames)

    return hist_df


def csv_to_dataframe_of_many_pairs (pairs, trading_type, interval)->list[pd.DataFrame]:
    """
    Provide a list of pairs, then call CSVFolderToDataFrame() above, and
    return dict of dataframe.
    Every pairs does not start at the same time, (e.g. BTC start in 2013 vs LUNA in 2019)
    So we make it (e.g. BTC dataframe shall start in 2019 like LUNA)
/*\ Warning read reference : /*\
/*\ https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-then-filling-it
    """
    market_history_df = {}
    minimum_date = np.datetime64("2001-01-01") #minimumDate is useful to cut every array
    #if type (pairs) != list:
    if not isinstance(pairs, list) :
        pairs = [pairs]
    for pair in pairs:
        market_history_df[pair] = csv_pair_folder_to_dataframe (pair, trading_type, interval)
        if minimum_date < market_history_df[pair]['Open Time'].iloc[0]:
            minimum_date = market_history_df[pair]['Open Time'].iloc[0]
    #every arrays will start with the same date.
    for pair in pairs:
        market_history_df[pair] =\
            market_history_df[pair].loc[(market_history_df[pair]['Open Time'] > minimum_date)]
        #for inplace=True, see (2)
        market_history_df[pair].set_index(['Open Time', 'Close Time'], inplace=True)
        market_history_df[pair]=market_history_df[pair].interpolate()

    return market_history_df


#Some testing functions
# def main():
    # test = st.pairsTrading()
    # checkCryptoVolume = {}
    # checkCryptoVolume['BTC']  = 100
    # checkCryptoVolume['USDT'] = 12000000
    # checkCryptoVolume['BNB']  = 5000
    # L = test.getPairsVolume(**checkCryptoVolume)
    # print ("L =", L)

    #dataretrieving test
    # f = os.path.dirname(os.path.realpath(__file__))+"\\"
    # paramScrap = {"folder": f,
    #               "years": en.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
    #               "trading_type": "spot",
    #               "symbols": L, "intervals": ['15m'],
    #               "startDate": "2017-01", "endDate": "2022-08",
    #               "checksum": True}
    # retrieveDatas (paramScrap)

    # CSV to DF test
    # hist_df = CSVFolderToDataFrame("BNBUSDT", "spot", "15m")
    # print(hist_df['Open Time'])
    # print ("fin ")


# main()

#References
#https://www.section.io/engineering-education/a-gentle-introduction-to-the-python-binance-api/
#https://stackoverflow.com/questions/57770943/python-keyerror-date-time
#NEVER grow a DataFrame row-wise!
#https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-then-filling-it
#(2) https://stackoverflow.com/questions/24041436/set-multiindex-of-an-existing-dataframe-in-pandas