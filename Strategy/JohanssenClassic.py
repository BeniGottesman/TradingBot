import datetime
import sys
import Strategy.Strategy as st
import Strategy.Strategystate as state
from typing import List
import maths.Statistics as statistics
import Portfolio.Portfolio as pf
import numpy as np
import pandas as pd
import Portfolio.PfState as pfstate

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
        self.__state__ = state.StrategyWaitToEntry(0,0)
        
        
    # c=0.75 -> mu +/- 0.75xsigma 
    # quotation = value of the different money now
    def doOneDay(self, timeNow: datetime, portfolio: pf.Portfolio, c: float, Moneys: list, quotations: np.array, verbose = False) -> None:
        timeSerieSize   = quotations.shape[0]
        nbShares        = quotations.shape[1]
        log_return = np.zeros(shape=(timeSerieSize, nbShares))

        # First we compute the spread
        for i in range (nbShares):
            # log_return[key] = np.array (stat.log_Transform(quotations[key]["Close"][beginningWindow:endWindow]))
            col = np.array (statistics.log_Transform(quotations[:,i]))
            log_return [:,i] = col
        
        # pd_lr_price_series = pd.DataFrame(index=quotations['Close Time'], data={key: log_return[key] for key in log_return})
        # pd_lr_price_series = pd_lr_price_series[-self.__rollingwindow__:]#we take only the last 30 days
        p = 1
        #log_return=pd.DataFrame(data={key: log_return[key] for key in log_return})
        jres = statistics.get_johansen(log_return, p)

        # if verbose :
        #     print ("There are", jres.r, "cointegration vectors")

        # v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
        spreadWeights = jres.evecr[:,0] # Weights to hold in order to make the mean reverting strat
        spreadWeights = spreadWeights/spreadWeights[0] #normalisation with the first crypto

        # Once I obtain the spread
        # I check the state of the pf
        error = 0.5
        #the state of the strategy
        presentStrategyState = self.__state__.getState() #string overload
        myMoney = portfolio.getBAL ()# Amount of money I  actually hold in my pf

        pfState = portfolio.getState()
        if pfState == "READY": #or # if pfState == pfstate.PortfolioIsReady():
            spread = spreadWeights * quotations[timeSerieSize-1,:] #= value
            alpha=1
            if myMoney>0:
                alpha  = spread/myMoney
            howMuchToInvestWeights = spreadWeights/alpha
            #Next line To delete ?
            howMuchToInvestWeights = howMuchToInvestWeights/nbShares
            
            mu      = np.mean (np.dot(log_return, howMuchToInvestWeights)) # Mean
            sigma   = np.var (np.dot(log_return, howMuchToInvestWeights)) # Variance
            sigma   = np.sqrt(sigma)
            spread  = np.dot (log_return, howMuchToInvestWeights) # The Spread or Portfolio to buy see research Spread
            
            dictOfInvestment={}
            dictOfQuotation={}
            i=0
            for key, value in zip(Moneys, howMuchToInvestWeights):
                dictOfInvestment[key] = value
                dictOfQuotation[key] = quotations[-1,i]
                i+=1
            portfolio.updateMarketQuotation(timeNow, dictOfQuotation)
            
            if presentStrategyState == "WaitToEntry":
                #if the last value of the mean reverting serie=spread[-1]<... then
                
                if spread[-1] < mu-c*sigma: #we start the Long strategy
                    self.__backtest__.entry(timeNow, dictOfInvestment)
                    pfValue = portfolio.getTCV()
                    self.__state__ = state.StrategyWaitToExit(timeNow, pfValue)
                if spread[-1] > mu+c*sigma: #we start the Short strategy
                    self.__backtest__.entry(timeNow, dictOfInvestment) # or -howMuchToInvestWeights ?
                    pfValue = portfolio.getTCV()
                    self.__state__ = state.StrategyWaitToExit(timeNow, pfValue)
            elif presentStrategyState == "WaitToExit":
                oldPfValue = self.__state__.getValue()
                pfValue = portfolio.getTCV()
                if spread[-1] < mu-c*sigma: #we exit the Short strategy
                    self.__backtest__.exit(timeNow)
                    self.__state__ = state.StrategyWaitToEntry(timeNow, pfValue)
                if spread[-1] > mu+c*sigma: #we exit the long strategy
                    self.__backtest__.exit(timeNow)
                    self.__state__ = state.StrategyWaitToEntry(timeNow, pfValue)
                    
                if pfValue*100/oldPfValue < 95:
                    self.__backtest__.exit(timeNow)
                    self.__state__ = state.StrategyWaitToEntry(timeNow, pfValue)
                    # self.__state__.setState("Nothing")
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

        # elif pfState == "StopLoss":
        #     if presentStrategyState == "WaitToExit":
        #             self.__backtest__.exit()
        #             self.__state__.setState("Nothing")

    #Vectorization
    #quotations: pd.DataFrame ?
    def doAlgorithm(self, portfolio: pf.Portfolio, c: float, quotations: dict, verbose = False) -> None:
            # timeIndex = quotations[0].index
            Moneys = list(quotations.keys())
            if len (Moneys) <= 0 :
                print("No money in your strategy.")
                return
            size = len(quotations[Moneys[0]]["Close"])
            # print("size=",size)
            
            n = portfolio.getNumberOfShares()
            nparray_quotations = np.zeros(shape=(self.__rollingwindow__, n))
            i=0
            while True:
                beginning = i
                end = self.__rollingwindow__ + i
                if end >= size:
                    break
                myShares = portfolio.getShares()
                j=0
                for key in myShares:
                    #We take the transpose
                    col = np.array (quotations [key]["Close"] [ beginning : end ]).T
                    nparray_quotations [:,j] = col
                    # q = np.concatenate ([q, col], axis=1)
                    j+=1
                timeNow = list (quotations[Moneys[0]]["Close Time"][ beginning : end ])[-1]
                self.doOneDay (timeNow, portfolio, c, Moneys, nparray_quotations, verbose)
                
                verbose = True
                if verbose and i%1000==0:
                    print("i =",i)
                    print(portfolio)
                    
                i+=1
            #portfolio.plot()
            