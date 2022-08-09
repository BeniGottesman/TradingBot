import enums as en
import os
import sys
import pandas as pd
fileDirectory = os.getcwd()
sys.path.append(fileDirectory+"binanceDataRetrieve\\")
from binanceDataRetrieve import downloadkline as dk
import enums as en

#Download the datas from binance.data, inside data folder and
def retrieveHistoricFromBinanceDatas (paramScrap):
    folder = paramScrap["folder"]
    years = paramScrap["years"]
    months = paramScrap["months"]
    symbols = paramScrap["symbols"]
    trading_type = paramScrap["trading_type"]
    intervals = paramScrap["intervals"]
    startDate = paramScrap["startDate"]
    endDate = paramScrap["endDate"]
    checksum = paramScrap["checksum"]
    for quoteCurrency in symbols: #quote currency
        num_symbols = len(symbols[quoteCurrency])
        dk.download_monthly_klines(trading_type, symbols[quoteCurrency], num_symbols, intervals, years, months, startDate, endDate, folder, checksum)

#convert a csv file into a dataframe
def CSVtoDataFrame (file)->pd.DataFrame:
    hist_df = pd.read_csv(file)
    hist_df.columns = en.HISTORICAL_BINANCE_COLUMN
    hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit='s')
    hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']/1000, unit='s')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)

    return hist_df
    
#This Function Take A pair, trading type = ''spot'', and an interval=''15m''
#then convert the csv file into a dataframe
#hist_df = CSVFolderToDataFrame("BNBUSDT", "spot", "15m")
def CSVPairFolderToDataFrame (pair, trading_type, interval,verbose=False)->pd.DataFrame:
    relative_path = "data\\"+trading_type+"\\monthly\\klines\\"+pair+"\\"+interval+"\\"

    #We now merge
    frames = []
    for file in os.listdir(relative_path):
       if file.endswith(".csv"):
            if(verbose):
                print ("merge = ", file)
            frames.append (CSVtoDataFrame(relative_path+file))
    hist_df = pd.concat(frames)
    
    return hist_df

#Provide a list of pairs, then call CSVFolderToDataFrame() above
#return dict of dataframe
def CSVToDataFrameOfManyPairs (pairs, trading_type, interval)->list:
    hist_df = {}
    if(type (pairs) != list):
        pairs = [pairs]
    for pair in pairs:
        hist_df[pair] = CSVPairFolderToDataFrame (pair, trading_type, interval)
    return hist_df


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
