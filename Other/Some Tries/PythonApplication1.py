# https://resilient-quant-trader.medium.com/scraping-crypto-currency-historical-data-from-binance-using-python-9c0e77c04df7

from binance import Client
import pandas as pd
import yaml
import datetime
import numpy as np
from functions import store_ohlcv

# import config
config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

# create client
client = Client(config['api_key'], config['api_secret'])

# import symbols from exchange infos
symbols = {symbol['symbol']:symbol for symbol in client.get_exchange_info()['symbols'] if symbol['isSpotTradingAllowed']}
# get through the 24h tickers and add quote_volume
for ticker in client.get_ticker():
    if ticker['symbol'] in symbols:
        symbols[ticker['symbol']]['quoteVolume'] = ticker['quoteVolume']
        
dic_symbols = {}
dic_symbols['BTC'] = [key for key,item in symbols.items() if float(item['quoteVolume'])>100 and item['quoteAsset']=='BTC']
print('BTC:',len(dic_symbols['BTC']))
dic_symbols['USDT'] = [key for key,item in symbols.items() if float(item['quoteVolume'])>12000000 and item['quoteAsset']=='USDT']
print('USDT:',len(dic_symbols['USDT']))
dic_symbols['BNB'] = [key for key,item in symbols.items() if float(item['quoteVolume'])>5000 and item['quoteAsset']=='BNB']
print('BNB:',len(dic_symbols['BNB']))

start_date = datetime.datetime(2020,1,1)
#intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
intervals = ['1h']
for quote in dic_symbols.keys():
    for symbol in dic_symbols[quote]:
        print(f"{datetime.datetime.now()} - downloading symbol {symbol} on {len(intervals)} intervals")
        for interval in intervals:
            try:
                store_ohlcv(client=client, symbol=symbol, interval=interval, start_date=start_date)
            except Exception as e:
                print(f'Error on {symbol}_{interval} because of {str(e)}')