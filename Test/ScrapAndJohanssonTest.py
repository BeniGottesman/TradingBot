from datetime import date
import os
import dataRetrieving as dr
import enums as cst
import numpy as np
import pandas as pd
import maths.Statistics as statistics
import backtest as bt
import matplotlib.pyplot as plt

def scrapandjohanssonTest():
    referencePair = 'BTCUSDT'
    checkCryptoVolume = {}
    # checkCryptoVolume['BTC']  = 100 #we want every pairs with base BTC such that the 24h-volume >500 
    checkCryptoVolume['USDT'] = 75000000
    # checkCryptoVolume['BNB']  = 1000

    #f = os.path.dirname(os.path.realpath(__file__))+"\\"
    paramScrap = {"folder": cst.ROOT_DIR,
                  "years": cst.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                  "trading_type": "spot", "intervals": ['15m'],
                  "startDate": "2017-01", "endDate": "2022-08",
                  "checksum": False}
    Iscrap = False #Turn to true for scrapping market datas
    L = bt.scrapDatas(checkCryptoVolume, paramScrap, Iscrap)

    #3rd I convert them into a dataframe
    print("To dataframe")
    pairs = L['USDT']
    data = dr.CSVToDataFrameOfManyPairs(pairs, 'spot', '15m')
    print("To dataframe: Done.")

    print("Johansen Test")
    log_return = {}
    thirtyDays = int ((60/15)*24*10) #How many '15-minutes' in thirty days

    #We start the strat by a log transform of the time-series
    for key in pairs:
        s = data [key]['Close']
        log_return[key] = np.array (statistics.log_Transform(s))
    
    #log return price series TO dataframe
    pd_lr_price_series = pd.DataFrame(index=data[referencePair]['Close Time'], data={key: log_return[key] for key in log_return})
    pd_lr_price_series = pd_lr_price_series[-thirtyDays:]#we take only the last 30 days
    p = 1 #p=1 -> 95%
    jres = statistics.get_johansen(pd_lr_price_series, p)

    print ("There are ", jres.r, "cointegration vectors")

    #v represents the weights for building the spread weights
    v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
    # v = v/v[0]
    # M = np.asmatrix (v)

    tmp = np.sum(np.abs (jres.evecr[:,0]))
    print (jres.evecr[:,0]/jres.evecr[0])

    # pd_lr_price_series = pd.DataFrame(index=data[referencePair]['Close Time'], data={key: log_return[key] for key in log_return} )
    timeline = pd_lr_price_series[referencePair].index
    #spread_average will be a vector of average
    #and draw a line which represents the mean (mean-reversion)
    spread_average  = np.mean (np.dot(pd_lr_price_series.values, v[1,:]/jres.evecr[0]))
    spread_average *= np.ones (len(timeline)) #we build a vector of one with size of timeline
    mu      = np.mean (np.dot(pd_lr_price_series.values, v[1,:]/jres.evecr[0])) # Mean
    sigma   = np.var (np.dot(pd_lr_price_series.values, v[1,:]/jres.evecr[0])) # Variance
    sigma   = np.sqrt(sigma)
    c=.50
    l1 = (mu+c*sigma)*np.ones (len(timeline))
    l2 = (mu-c*sigma)*np.ones (len(timeline))
    spread = np.dot(pd_lr_price_series.values, v[1,:]/jres.evecr[0])
    
    print ("Plot")
    plt.plot(timeline, spread, timeline, spread_average, timeline, l1, timeline, l2)
    plt.gcf().autofmt_xdate()
    plt.plot()
    plt.show()