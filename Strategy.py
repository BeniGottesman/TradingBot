import BinanceClient as bc
from datetime import date
import os
import dataRetrieving as dr
import enums as en
import numpy as np

clienSingletonInstance = bc.client()
client = clienSingletonInstance.getClient()

class pairsTrading:
    def __init__(self):
        return

    def createPf(self):
        return

    def pairsSelection(self):
        return

    #We provide a dict checkCryptoVolume['BTC']  = 100 and return every pairs XXXBTC such that the volume is over 100 last 24h
    def getPairsVolume(self, **asset)-> dict:
        # import symbols from exchange infos
        symbols = {}
        for symbol in client.get_exchange_info()['symbols']:
            if symbol['isSpotTradingAllowed']==True:
                symbols [symbol['symbol']] = symbol

        # get through the 24h tickers and add quote_volume
        for ticker in client.get_ticker():
            if ticker['symbol'] in symbols: #i.e. isSpotTradingAllowed
                symbols[ticker['symbol']]['quoteVolume'] = ticker['quoteVolume'] #we add a quoteVolume key to the dictionnary
                
        dic_symbols = {}
        #LTCBTC = LTC = Base Asset, BTC = Quote Asset
        for qA in asset:#qA=Quote Asset
            dic_symbols[qA] = 0
            pair = [] #exemple BTCUSDT
            for key,item in symbols.items(): 
                bA = item['baseAsset']
                if float(item['quoteVolume'])> float(asset[qA]) and item['quoteAsset']==qA:
                    pair.append(bA+qA)
            dic_symbols[qA] = pair
            print(qA,':', len(dic_symbols[qA]))

        return dic_symbols

        # start_date = date.datetime(2020,1,1)
        # intervals = ['1h']
        # for quote in dic_symbols.keys():
        #     for symbol in dic_symbols[quote]:
        #         print(f"{date.datetime.now()} - downloading symbol {symbol} on {len(intervals)} intervals")
        #         for interval in intervals:
        #             try:
        #                 store_ohlcv(client=client, symbol=symbol, interval=interval, start_date=start_date)
        #             except Exception as e:
        #                 print(f'Error on {symbol}_{interval} because of {str(e)}')

    def plotResult(self):
        return

#checkCryptoVolume contain the crypto and the 24h-volume minimum to download
#paramScrap contain every parameters for scrapping
def scrapDatas (checkCryptoVolume: dict, paramScrap: dict)-> dict:
    #1st we check the market with high exchange volume
    strat = pairsTrading()
    L = strat.getPairsVolume(**checkCryptoVolume)
    print(L)

    #2nd I scrap the datas with the desired 24h-volume
    paramScrap["symbols"]=L
    dr.retrieveHistoricFromBinanceDatas (paramScrap)

    return L

def main ():
    checkCryptoVolume = {}
    checkCryptoVolume['BTC']  = 500 #we want every pairs with base BTC such that the 24h-volume >500 
    checkCryptoVolume['USDT'] = 100000000
    checkCryptoVolume['BNB']  = 5000

    f = os.path.dirname(os.path.realpath(__file__))+"\\"
    paramScrap = {"folder": f,
                  "years": en.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                  "trading_type": "spot", "intervals": ['15m'],
                  "startDate": "2017-01", "endDate": "2022-08",
                  "checksum": True}
    L = scrapDatas(checkCryptoVolume, paramScrap)

    #3rd I convert them into a dataframe
    # pairs = L['USDT']
    # hist = dr.CSVToDataFrameOfManyPairs(pairs[5], 'spot', '15m')
    # print(hist)



main()