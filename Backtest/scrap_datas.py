from datetime import date
import os
import binance_data.data_retrieving as dr
import binance_data.csv_to_data as cd
import enums as cst
import numpy as np
import pandas as pd
import binance_data.scrap_datas as bt
import matplotlib.pyplot as plt

def scrap_every_USDT_datas():
    checkCryptoVolume = {}
    # = 100 #we want every pairs with base BTC such that the 24h-volume >500 
    checkCryptoVolume['USDT'] = 1

    #f = os.path.dirname(os.path.realpath(__file__))+"\\"
    paramScrap = {"folder": cst.ROOT_DIR,
                  "years": cst.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                  "trading_type": "spot", "intervals": ['15m'],
                  "startDate": "2017-01", "endDate": "2022-08",
                  "checksum": False}
    Iscrap = True #Turn to true for scrapping market datas
    L = bt.scrap_datas(checkCryptoVolume, paramScrap, Iscrap)

    #3rd I convert them into a dataframe
    print("To dataframe")
    pairs = L['USDT']
    cd.csv_to_dataframe_of_many_pairs(pairs, 'spot', '15m')
    print("To dataframe: Done.")
