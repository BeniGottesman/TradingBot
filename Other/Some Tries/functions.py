from binance import Client
import pandas as pd
import yaml
import datetime
import numpy as np
import os

def store_ohlcv(client, symbol="BTCUSDT", interval='4h', start_date=datetime.datetime(2021,1,1)):
    # import ohlcv from binance starting from date 'start_date', that has to be in a string format of the timestamp in ms
    start_str = str(1000*start_date.timestamp())
    klines = client.get_historical_klines_generator(symbol, interval, start_str)
    # create the DataFrame
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'end_time', 'quote_volume', 'nbs_trades', 'buy_base_volume', 'buy_quote_volume', 'ignore'])
    # add data
    df.loc[:,'date'] = pd.to_datetime(df.time, unit='ms')
    # remove the useless column and the last row as it is the current candle, therefore is not completed
    df = df.drop('ignore', axis=1).iloc[:-1]
  
    #Create the data's directory
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    directory = "data"
    path = os.path.join(parent_dir, directory)
    isFile = os.path.isdir(path)
    if isFile == False:
        os.mkdir(path)
    
    # store data as a pkl file
    df.to_pickle(f"data/{symbol}_{interval}.pkl")