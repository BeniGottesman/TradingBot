import urllib.request
import zipfile
import os 
from pathlib import Path
import pandas as pd
from pyparsing import col

#import DataRetrieving as dr
def _retrieveDatas_ (pairs):
    market      = 'spot'
    dataType    = 'monthly'
    date        = '2022-06'
    frequency   = '5m'
    print ("L =", pairs)
    for qC in pairs: #quote currency
        QuoteCurrency = qC
        for bC in pairs[qC]: #base currency
            BaseCurrency = bC.replace(qC,'')
            retrieveBinanceDatas (market, dataType, BaseCurrency, QuoteCurrency, frequency, date)


def retrieveBinanceDatas (market, dataType, 
                        baseCurrency, quoteCurrency, 
                        frequency, date, futuresUSDTorCoin='um'):
    fileName = baseCurrency+quoteCurrency+'-'+frequency+'-'+date
    fileNameZip= fileName+'.zip'
    filenameCSV= fileName+'.csv'

    if market == "futures":
        market+'/'+futuresUSDTorCoin

    url = 'https://data.binance.vision/data/'
    url += market+'/'+dataType+'/klines/'+baseCurrency+quoteCurrency+'/'
    url += frequency+'/'+fileNameZip
    print ("Retrieving url file = ", url)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    directory_to_extract_to = dir_path+'\datas\\'+market+'\\'+dataType+'\\'+baseCurrency+quoteCurrency+'\\'+frequency

    my_file = Path(directory_to_extract_to+'\\'+filenameCSV)
    if my_file.exists():
        print(filenameCSV)
        print('File already exists.')
        return

    try:
        filehandle, _ = urllib.request.urlretrieve(url)
    except Exception:
        print("url Not Valid ?")
        return
    with zipfile.ZipFile(filehandle, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)


def CSVtoDataFrame (file):
    hist_df = pd.read_csv(file)
    hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
    hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit='s')
    hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']/1000, unit='s')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
    
    return hist_df

# def main():
    # file = "C:\\Users\\benig\\Documents\\Projects\\TradingBot\\datas\\Spot\\Daily\\BTCUSDT\\30m\BTCUSDT-30m-2022-07-12.csv"
    # df = dr.CSVtoDataFrame(file)
    #print (df)

    # market = 'spot'
    # dataType = 'monthly'
    # BaseCurrency = 'BTC'
    # QuoteCurrency = 'USDT'
    # date = '2022-06'

    # tmpinterval = Constants.daily_intervals
    # if dataType == 'monthly':
    #     tmpinterval = Constants.monthly_intervals

    # for frequency in tmpinterval:
    #     dr.retrieveBinanceDatas (market, dataType, BaseCurrency, QuoteCurrency, frequency, date)