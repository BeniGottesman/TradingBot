import BinanceClient as bc
from datetime import date
import os
import dataRetrieving as dr
import enums as en
import numpy as np
import pandas as pd
import maths.Statistics as stat
import backtest as bt
import matplotlib.pyplot as plt

clienSingletonInstance = bc.client()
client = clienSingletonInstance.getClient()



def main ():
    referencePair = 'BTCUSDT'
    checkCryptoVolume = {}
    # checkCryptoVolume['BTC']  = 100 #we want every pairs with base BTC such that the 24h-volume >500 
    checkCryptoVolume['USDT'] = 100000000
    # checkCryptoVolume['BNB']  = 1000

    f = os.path.dirname(os.path.realpath(__file__))+"\\"
    paramScrap = {"folder": f,
                  "years": en.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                  "trading_type": "spot", "intervals": ['15m'],
                  "startDate": "2017-01", "endDate": "2022-08",
                  "checksum": False}
    Iscrap = False
    L = bt.scrapDatas(checkCryptoVolume, paramScrap, Iscrap)

    #3rd I convert them into a dataframe
    print("To dataframe")
    pairs = L['USDT']
    data = dr.CSVToDataFrameOfManyPairs(pairs, 'spot', '15m')
    print("To dataframe: Done.")

    print("Johansen Test")
    p = 1
    log_return = {}
    
    for key in pairs:
        s = data [key] ['Close']
        log_return[key] = np.array (stat.log_Transform(s))
    
    y = pd.DataFrame(index=data[referencePair]['Close Time'], data={key: log_return[key] for key in log_return})
    
    jres = stat.get_johansen(y, p)

    print ("There are ", jres.r, "cointegration vectors")

    v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
    # M = np.asmatrix (v)

    pd_lr_price_series = pd.DataFrame(index=data[referencePair].index, data={key: log_return[key] for key in log_return} )
    spread_average = np.mean (np.dot(pd_lr_price_series.values, v[1,:]))
    spread_average *= np.ones(len(data[referencePair]['Close Time']))#it will be a vector of average
    spread = np.dot(pd_lr_price_series.values, v[1,:])

    print (spread_average)
    plt.plot(data[referencePair]['Close Time'], spread, data[referencePair]['Close Time'], spread_average)
    plt.gcf().autofmt_xdate()
    plt.plot()
    plt.show()

main()