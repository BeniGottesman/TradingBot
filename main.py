import BinanceClient as bc
from datetime import date
import os
import dataRetrieving as dr
import enums as en
import numpy as np
import pandas as pd
import maths.Statistics as stat
import backtest as bt

clienSingletonInstance = bc.client()
client = clienSingletonInstance.getClient()



def main ():
    checkCryptoVolume = {}
    checkCryptoVolume['BTC']  = 500 #we want every pairs with base BTC such that the 24h-volume >500 
    checkCryptoVolume['USDT'] = 500000000
    checkCryptoVolume['BNB']  = 5000

    f = os.path.dirname(os.path.realpath(__file__))+"\\"
    paramScrap = {"folder": f,
                  "years": en.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                  "trading_type": "spot", "intervals": ['15m'],
                  "startDate": "2017-01", "endDate": "2022-08",
                  "checksum": True}
    L = bt.scrapDatas(checkCryptoVolume, paramScrap)

    #3rd I convert them into a dataframe
    print("To dataframe")
    pairs = L['USDT']
    data = {}
    for pair in pairs:
        data[pair] = dr.CSVToDataFrameOfManyPairs(pair, 'spot', '15m')
    # print(hist)
    print("Done.")

    print("Johansen Test")
    p = 1

    log_return = {}
    for key, value in data.items():
        # print(value["BTCUSDT"].columns.tolist())
        s = pd.value ["BTCUSDT"]["Close"]
        log_return[key] = np.array (stat.log_Transform(s))
    
    y = pd.DataFrame(index=data['BTCUSDT'].index, data={key: log_return[key] for key in log_return})
    
    jres = stat.get_johansen(y, p)

    print ("There are ", jres.r, "cointegration vectors")

    v =  np.array ([np.ones(3), jres.evecr[:,0], jres.evecr[:,1]])
    M = np.asmatrix (v)
    print(v)



main()