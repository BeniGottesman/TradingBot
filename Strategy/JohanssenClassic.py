import sys
import Strategy.Strategy as st
import Strategy.Strategystate as state
from typing import List
import maths.Statistics as stat
import Portfolio.Portfolio as pf
import numpy as np
import pandas as pd

class JohannsenClassic(st.Strategy):
    def __init__(self, portfolio: pf.Portfolio,
                 _daysrollingwindow: int, _timeCycleInSecond: int, _initialInvestmentPercentage : float,
                 _transactionCost: float, _name="generic portfolio") -> None:
        self.__timeCycleInSecond__ = _timeCycleInSecond #15mn=15*60 for instance
        self.__rollingwindowindays__ = _daysrollingwindow #=30 days for instance
        self.__rollingwindow__ = int ((60/(self.__timeCycleInSecond__/60))*24*_daysrollingwindow)
        self.__transactionCost__ = _transactionCost
        self.__backtest__ = st.BacktestCommand(portfolio)
        if _initialInvestmentPercentage > 1 or _initialInvestmentPercentage < 0:
            sys.exit()
        self.__initialInvestmentPercentage__ = _initialInvestmentPercentage #0.2% of the capital for instance
        self.__state__ = state.StrategyWaitToEntry()

    def doAlgorithm(self, portfolio: pf.Portfolio, c: int, quotations: dict, verbose = False) -> None:
        log_return = {}

        # First we compute the spread
        myShares = portfolio.getShares()
        for key, value in myShares.items:
            log_return[key] = np.array (stat.log_Transform(quotations[key]))
        
        # pd_lr_price_series = pd.DataFrame(index=quotations['Close Time'], data={key: log_return[key] for key in log_return})
        # pd_lr_price_series = pd_lr_price_series[-self.__rollingwindow__:]#we take only the last 30 days
        p = 1
        jres = stat.get_johansen(log_return, p)

        if verbose :
            print ("There are ", jres.r, "cointegration vectors")

        # v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
        spreadWeights = jres.evecr[:,0]
        spreadWeights = spreadWeights/spreadWeights[0] #normalisation

        # spread  = np.dot(pd_lr_price_series.values, v[1,:])
        mu      = np.mean (np.dot(log_return.values, spreadWeights[1,:]))
        sigma   = np.var (np.dot(log_return.values, spreadWeights[1,:]))

        # Once I obtain the spread
        # I check the state of the pf
        error = 0.5
        presentState = self.__state__.getState() #string overload
        weightArrayOfShares = portfolio.getWeightArrayOfShares()
        S = portfolio.getTCV()
        NbShares = portfolio.getNumberOfShares()
        howMuchToInvestWeights = spreadWeights*(S/NbShares)*log_return [-1]
        pfState = portfolio.getState()
        if pfState == "Ready":
            if presentState == "WaitToEntry":
                if S < mu-c*sigma: #we start the strategy
                    self.__backtest__.entry(howMuchToInvestWeights)
                    self.__state__ = state.StrategyWaitToExit()
            if presentState == "WaitToExit":
                if S > mu+c*sigma: #we exit the strategy
                    self.__backtest__.exit()
                    self.__state__ = state.StrategyWaitToEntry()
                elif howMuchToInvestWeights-weightArrayOfShares > error:
                    if pfState == "Ready":
                        rebalancing = weightArrayOfShares - spreadWeights
                        self.__backtest__.entry(rebalancing)
                    if pfState == "No Money in BAL" and verbose:
                        print ("No money to rebalance the Portfolio")

        if pfState == "StopLoss":
            if presentState == "WaitToExit":
                    self.__backtest__.exit()
                    self.__state__.setState("Nothing")
