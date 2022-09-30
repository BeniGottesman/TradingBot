import os
import string
import sys
import pandas as pd
import numpy as np

fileDirectory = os.getcwd()
sys.path.append(fileDirectory+"binanceDataRetrieve\\")
from binance_data import download_kline as dk
import enums as cst

def csv_to_dataframe (file: string)->pd.DataFrame:
    """
    Convert a csv file into a pickle and DataFrame.
    """
    filepkl = file.split(".")[0]+".pkl" #pickle is for reading quickly the csv
    # if not os.path.exists(filepkl):
    hist_df = pd.read_csv(file)
    hist_df.columns = cst.HISTORICAL_BINANCE_COLUMN
    #As dates are returned from Binance as timestamps,
    #we first divide by 1000 and then set the units to seconds to convert correctly.
    hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit='s')
    #To delete the millisecond
    hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']).dt.floor('S')
    hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']/1000, unit='s')
    hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']).dt.floor('S')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume',
                       'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
    #We convert our objects into numerical values using the to_numeric function.
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)

    hist_df.set_index(['Open Time', 'Close Time'], inplace=True)

    hist_df.to_pickle(filepkl) #PICKLE
    os.remove(file)

    return hist_df

#hist_df = CSVFolderToDataFrame("BNBUSDT", "spot", "15m")
def csv_pair_folder_to_dataframe (pair: string,
                                  trading_type: string,
                                  interval: string, verbose=False)->pd.DataFrame:
    """
    This Function Take A pair, trading type = ''spot'', and an interval=''15m''.
    Then convert the csv file into a dataframe.
    """
    relative_path = "data\\"+trading_type+"\\monthly\\klines\\"+pair+"\\"+interval+"\\"

    #We now merge
    tmp_frames = {}
    tmp_int_dates = []
    for file in os.listdir(relative_path):
        tmp_date = file
        tmp_date = tmp_date.replace(pair,'').replace(interval,'')\
            .replace('.pkl','').replace('.csv','').replace('-','')
        tmp_int_dates.append (int(tmp_date))
        if file.endswith(".csv"):
            if verbose:
                print ("merge = ", file)
            tmp_frames[int(tmp_date)]= (csv_to_dataframe(relative_path+file))
        elif file.endswith(".pkl"):
            tmp_frames[int(tmp_date)]= (pd.read_pickle(relative_path+file))

    tmp_int_dates.sort()
    frames = []
    for d in tmp_int_dates:
        frames.append(tmp_frames[d])

    hist_df = pd.concat(frames)

    return hist_df


#add minimum time, in scrapdata
def csv_to_dataframe_of_many_pairs (pairs: string,
                                    trading_type: string,
                                    interval: string)->list[pd.DataFrame]:
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
        if minimum_date < market_history_df[pair].index.get_level_values('Close Time')[0]:
            minimum_date = market_history_df[pair].index.get_level_values('Close Time')[0]
    #every arrays will start with the same date.
    for pair in pairs:
        market_history_df[pair] =\
            market_history_df[pair]\
                .loc[(market_history_df[pair].index.get_level_values('Close Time') > minimum_date)]

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
#(3) https://stackoverflow.com/questions/28371308/sort-by-column-within-multi-index-level-in-pandas
