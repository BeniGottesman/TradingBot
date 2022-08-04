import numpy as np
import pandas as pd
#https://nbviewer.org/github/mapsa/seminario-doc-2014/blob/master/cointegration-example.ipynb
from statsmodels.tsa.vector_ar.vecm import coint_johansen
#https://www.statsmodels.org/stable/examples/notebooks/generated/stationarity_detrending_adf_kpss.html?highlight=adf
from statsmodels.tsa.stattools import adfuller


def get_johansen(y, p):

        """
        Get the cointegration vectors at 95% level of significance
        given by the trace statistic test.
        """

        N, col = y.shape
        jres = coint_johansen(y, 0, p)
        trstat = jres.lr1                       # trace statistic
        tsignf = jres.cvt                       # critical values

        j=2
        for i in range(col):
            if trstat[i] > tsignf[i, j]:     # 0: 90%  1:95% 2: 99%
                r = i + 1
        jres.r = r
        jres.evecr = jres.evec[:, :r]

        return jres

def DickeyFullerCointegrationTest():
    p = 1

    log_return_BTC = np.array (log_Transform(data ['BTCUSDT'].close))
    log_return_ETH = np.array (log_Transform(data ['ETHUSDT'].close))
    log_return_BNB = np.array (log_Transform(data ['BNBUSDT'].close))
    #log_return = np.array ( [log_return, np.array (log_Transform(data ['ETHUSDT'].close))] )
    y = pd.DataFrame(index=data['BTCUSDT'].index, data={'BTCUSDT': log_return_BTC, 'ETHUSDT': log_return_ETH, 'BNBUSDT': log_return_BNB} )
    #print (log_return)
    jres = get_johansen(y, p)

    print ("There are ", jres.r, "cointegration vectors")

    v =  np.array ([np.ones(3), jres.evecr[:,0], jres.evecr[:,1]])
    M = np.asmatrix (v)
    print(v)

def ADFUnitRootTest ():
    pvalue = 0.0001
    i = 0
    statresult = {}
    dfoutput = {}
    for sym in Big_Volume_Symbols:
        #We do a log-return
        log_return = log_Transform(data [sym].close)
        
        #perform augmented Dickey-Fuller test
        statresult[sym] = adfuller(log_return, autolag="AIC")
        dfoutput[sym] = pd.Series(
            statresult[sym][0:4],
            index=[
                "Test Statistic",
                "p-value",
                "#Lags Used",
                "Number of Observations Used",
            ],
        )
        #We build the sub-series with the critical values
        for key, value in statresult[sym][4].items():
            dfoutput[sym]["Critical Value (%s)" % key] = value

        #if dfoutput[sym]["Critical Value (10%)"] > dfoutput[sym]['Test Statistic'] :
        if float (dfoutput[sym]["p-value"]) < pvalue :
            i += 1
            #print(dfoutput[sym])
            print(i, ". Symbol = ", sym, ", p-value = ", float (dfoutput[sym]["p-value"]))

def nan_helper(y):
#    """Helper to handle indices and logical indices of NaNs.

#    Input:
#        - y, 1d numpy array with possible NaNs
#    Output:
#        - nans, logical indices of NaNs
#        - index, a function, with signature indices= index(logical_indices),
#          to convert logical indices of NaNs to 'equivalent' indices
#    Example:
#        >>> # linear interpolation of NaNs
#        >>> nans, x= nan_helper(y)
#        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
#    """

    return np.isnan(y), lambda z: z.to_numpy().nonzero()[0]

def log_Transform (data):
#    """Helper to handle indices and logical indices of NaNs.

#    Input:
#        - data, 1d numpy array with possible NaNs
#    Output:
#        - log return, 1d
#    Example:
#        >>> log_return = log_Transform(data [sym].close)
#    """
    log_return = np.log(data) - np.log(data.shift(1))
    nans, x = nan_helper(log_return)
    log_return[nans] = np.interp(x(nans), x(~nans), log_return[~nans])
    return log_return