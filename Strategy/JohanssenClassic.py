import datetime
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
                 _transactionCost: float, _name="generic strategy") -> None:
        self.__timeCycleInSecond__ = _timeCycleInSecond #15mn=15*60 for instance
        self.__rollingwindowindays__ = _daysrollingwindow #=30 days for instance
        self.__rollingwindow__ = int ((60/(self.__timeCycleInSecond__/60))*24*_daysrollingwindow)
        self.__transactionCost__ = _transactionCost
        self.__backtest__ = st.BacktestCommand(portfolio)
        if _initialInvestmentPercentage > 1 or _initialInvestmentPercentage < 0:
            sys.exit()
        #This variable is 1 i.e. not used yet
        self.__initialInvestmentPercentage__ = _initialInvestmentPercentage #0.2% of the capital for instance
        self.__state__ = state.StrategyWaitToEntry()
        
        
    # c=0.75 -> mu +/- 0.75xsigma 
    # quotation = value of the different money now
    def doOneDay(self, timeNow: datetime, portfolio: pf.Portfolio, c: float, quotations: dict, verbose = False) -> None:
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
        spreadWeights = jres.evecr[:,0] # Weights to hold in order to make the mean reverting strat
        spreadWeights = spreadWeights/spreadWeights[0] #normalisation with the first crypto

        # Once I obtain the spread
        # I check the state of the pf
        error = 0.5
        #the state of the strategy
        presentStrategyState = self.__state__.getState() #string overload
        myMoney = portfolio.getTCV ()# Amount of money I actually hold in my pf
        #NbShares = portfolio.getNumberOfShares()# numbers of shares I hold
        NbShares = len(spreadWeights) # array containing numbers of shares I hold

        #we renormalize the weights w.r.t. the pf money
        spread = spreadWeights * quotations #= value
        alpha = spread/myMoney
        howMuchToInvestWeights = spreadWeights/alpha
        
        mu      = np.mean (np.dot(log_return.values, howMuchToInvestWeights)) # Mean
        sigma   = np.var (np.dot(log_return.values, howMuchToInvestWeights)) # Variance
        sigma   = np.sqrt(sigma)
        spread  = np.dot (log_return.values, howMuchToInvestWeights) # The Spread or Portfolio to buy see research Spread

        pfState = portfolio.getState()
        if pfState == "Ready":
            if presentStrategyState == "WaitToEntry":
                #if the last value of the mean reverting serie=spread[-1]<... then
                if spread[-1] < mu-c*sigma: #we start the Long strategy
                    self.__backtest__.entry(timeNow, howMuchToInvestWeights)
                if spread[-1] > mu+c*sigma: #we start the Short strategy
                    self.__backtest__.entry(timeNow, howMuchToInvestWeights) # or -howMuchToInvestWeights ?
                self.__state__ = state.StrategyWaitToExit()
            if presentStrategyState == "WaitToExit":
                if spread[-1] < mu-c*sigma: #we exit the Short strategy
                    self.__backtest__.exit()
                    self.__state__ = state.StrategyWaitToEntry()
                if spread[-1] > mu+c*sigma: #we exit the long strategy
                    self.__backtest__.exit()
                    self.__state__ = state.StrategyWaitToEntry()
            #####Hedging : If we want to buy the spread#####
            #####Add this update in a new version#####
            ##### elif howMuchToInvestWeights-weightArrayOfShares > error: -> Not true, substraction of 2 arrays
                # elif newSpread - myPf_oldSpread > error: #Better
                #     if pfState == "Ready":                
                #         weightArrayOfShares = portfolio.getWeightArrayOfShares()
                #         rebalancing = weightArrayOfShares - spreadWeights
                #         self.__backtest__.entry(rebalancing)
                #     if pfState == "No Money in BAL" and verbose:
                #         print ("No money to rebalance the Portfolio")

        if pfState == "StopLoss":
            if presentStrategyState == "WaitToExit":
                    self.__backtest__.exit()
                    self.__state__.setState("Nothing")

    #Vectorization
    def doAlgorithm(self, portfolio: pf.Portfolio, c: float, quotations: pd.DataFrame, verbose = False) -> None:
            # timeIndex = quotations[0].index
            size = len(quotations.index)
            for i in size:
                #j = i * self.__timeCycleInSecond__ # We convert it to timestamp
                beginning = i*self.__rollingwindow__
                end = (i+1)*self.__rollingwindow__ + 1
                q = quotations.iloc [ beginning : end ]
                timeNow = q.index [-1]
                self.doOneDay (self, timeNow, portfolio, c, q, verbose)
            portfolio.plot()
            