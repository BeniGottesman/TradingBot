from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd

apikey = 'P6292qJXnqQ8OnoVTGmrQTOeL7ITxPadzp2Kmn8voLDgf8hUjUZAOll3jqWNaYQg'
apisecret = 'vOXpLeLba3YT1XmN5VFFLARoqDSowLTSatKVfBNLvbXX0EClqZ7EYyBjx3VJKJrX'

#Performing authentication
client = Client(apikey, apisecret)

VScurrency1 = "USDT"
VScurrency2 = "USD"

#get symbols
exchange_info = client.get_exchange_info()
dfexchange_info_symbols = pd.DataFrame (exchange_info['symbols'])
i=0
dfexchange_info_symbolsUSD = dfexchange_info_symbols [dfexchange_info_symbols.symbol.str.contains(VScurrency1)==True]
for s in exchange_info['symbols']:
    if VScurrency2 in s['symbol'] or VScurrency1 in s['symbol']:
        i+= 1
        #print(s['symbol'])
print (i)

#Getting ticker data
tickers = client.get_all_tickers()
ticker_dataframe = pd.DataFrame(tickers)
ticker_dataframe.head()
