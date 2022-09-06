import BinanceClient as bc
from datetime import date
import os
import dataRetrieving as dr
import enums as cst
import numpy as np
import pandas as pd
import maths.Statistics as stat

clienSingletonInstance = bc.client()
client = clienSingletonInstance.getClient()

#checkCryptoVolume contain the crypto and the 24h-volume minimum to download
#paramScrap contain every parameters for scrapping
def scrapDatas (checkCryptoVolume: dict, paramScrap: dict, scrap=False)-> dict:
    #1st we check the market with high exchange volume
    L = getPairsVolume(**checkCryptoVolume)
    print(L)

    #2nd I scrap the datas with the desired 24h-volume
    paramScrap["symbols"]=L
    if scrap:
        dr.retrieveHistoricFromBinanceDatas (paramScrap)

    return L

#We provide a dict checkCryptoVolume['BTC']  = 100 and return every pairs XXXBTC such that the volume is over 100 last 24h
def getPairsVolume(**asset)-> dict:
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