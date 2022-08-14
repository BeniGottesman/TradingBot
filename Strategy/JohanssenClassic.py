import sys
import Strategy.Strategy as st
from typing import List
import maths.Statistics as stat
import Portfolio.Portfolio as pf
import numpy as np
import pandas as pd

class JohannsenClassic(st.Strategy):
    def __init__(self, portfolio: pf.Portfolio,
                 _daysrollingwindow: int, _timeCycle: int, _initialInvestmentPercentage : float,
                 _transactionCost: float, _name="generic portfolio") -> None:
        self.__timeCycle__ = _timeCycle #15mn for instance
        self.__daysrollingwindow__ = _daysrollingwindow #=30 days for instance
        self.__rollingwindow__ = int ((60/self._timeCycle)*24*_daysrollingwindow)
        self.__transactionCost__ = _transactionCost
        self.__backtest__ = st.BacktestCommand(portfolio)
        if _initialInvestmentPercentage > 1 or _initialInvestmentPercentage < 0:
            sys.exit()
        self.__initialInvestmentPercentage__ = _initialInvestmentPercentage #0.2% of the capital for instance

    def doAlgorithm(self, portfolio: pf.Portfolio, c: int, quotations: List, verbose = False) -> None:
        log_return = {}

        # First we compute the spread
        myShares = portfolio.getShares()
        for key, value in myShares.items:
            log_return[key] = np.array (stat.log_Transform(value))
        
        pd_lr_price_series = pd.DataFrame(index=quotations['Close Time'], data={key: log_return[key] for key in log_return})
        pd_lr_price_series = pd_lr_price_series[-self.__rollingwindow__:]#we take only the last 30 days
        p = 1
        jres = stat.get_johansen(pd_lr_price_series, p)

        if verbose :
            print ("There are ", jres.r, "cointegration vectors")

        # v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
        spreadWeights = jres.evecr[:,0]
        # v/-v[0]

        # spread  = np.dot(pd_lr_price_series.values, v[1,:])
        mu      = np.mean (np.dot(pd_lr_price_series.values, v[1,:]))
        sigma   = np.var (np.dot(pd_lr_price_series.values, v[1,:]))

        # Once I obtain the spread
        # I check the state of the pf
        error = 0.5
        presentState = self.__state__.getState()
        if portfolio.getState() == "Ready":
            if presentState == "waitToEntry":
                if portfolio.getTCV < mu-c*sigma: #we start the strategy
                    self.__backtest__.entry(spread)
                    self.__state__.setState("WaitToExit") 
            if presentState == "WaitToExit":
                if portfolio.getTCV > mu+c*sigma: #we exit the strategy
                    self.__backtest__.exit()
                    self.__state__.setState("Nothing")
                elif spread-portfolio.getTCV > error and portfolio.getState() == "Money":
                    rebalancing = portfolio.weight-spread
                    self.__backtest__.entry(rebalancing)

        if portfolio.getState() == "Ready":
            if self.__state__ == "Entry":

        return 1

    