"""Portfolio.py"""

import string
from typing import List
from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame
import BinanceClient
from datetime import date


class AbstractPortfolio:
    quoteCurrency: string
    #Why I am not using a Dataframe: 
    #https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-then-filling-it
    assets: List #list of str assets hold assets = [BTC, ETH, ...]
    transactions: dict #transaction[BTC][datetime]-> [hold, Spot/Future, Strategy, price in USDT]
    balance: dict #balance[Date]=value of the pf in USDT
    value: List

    def __init__(self, _quoteCurrency: string):
        self.assets = []
        self.transactions = {}
        self.quoteCurrency = _quoteCurrency

    def sell(self, date, asset, qty):#virtual pure
        pass

    def buy(self, date, asset, qty):#virtual pure
        pass
    
    def dataFrame(self):
        return #dataframe of portfolio

    def addAsset(self, A: str):
        self.assets.append(A)

    def removeAsset(self, A: str):
        self.assets.remove(A)

    #return the actual value of the portfolio
    def pfValue (self):
        client = BinanceClient.client.getClient()
        tmpValue = 0
        fee = 0.001
        for a in self.assets:
            price = client.get_symbol_ticker(symbol=a)
            lastvalue = list(self.value[a])[-1]
            tmpValue = price*lastvalue*(1.0-fee)

    #return the value of the portfolio at date
    def pfValue (self, date=date.datetime()):
        return

    def plotHistory (self):
        #Sum each column:
        PnL = self.transactions.sum(axis=0)
        
        plt.plot(self.transactions.index, PnL)
        plt.show()

    def plotAssetTransactions(self, asset):
        plt.plot(self.transactions[asset].keys(), self.transactions[asset])
        plt.show()
    
    def plot (self):
        self.plotHistory (self)

    def expectedReturn(self)-> np.float64:
        return 0.0

    def volatility(self)-> np.float64:
        return 0.0

    def sharpeRatio(self)-> np.float64:
        #Sharpe Ratio = (Rp – Rf) / Standard deviation
        #Rp = expected return (or actual return for historical calculations) on the asset or the portfolio being measured.
        #risk free rate
        return self.expectedReturn(self)/self.volatility(self)

    def addAsset (self, _a: str):
        self.assets.append(_a)
        #add 0 transaction ?

    def numberOfAssets (self):
        return len(self.assets)


class BacktestPortfolio(AbstractPortfolio):
    def __init__(self, _quoteCurrency: string):
        super(self, _quoteCurrency).__init__()

    def sell(self, date, asset, qty):
        self.transactions[asset][date] = qty
        lastvalue = list(self.value[asset])[-1]
        self.value[asset][date] = lastvalue - qty #2d-dictionary
        print (date,". ", asset ,"Sell = ", qty, 
                ", Hold = ", self.value[asset][date])

    def buy(self, date, asset, qty):
        self.transactions[asset][date] = qty
        lastvalue = list(self.value[asset])[-1]
        self.value[asset][date] = lastvalue + qty
        print (date,". ", asset ,"Buy = ", qty, 
                ", Hold = ", self.value[asset][date])


class TradingPortfolio(AbstractPortfolio):
    def __init__(self, _quoteCurrency: string):
        super(self, _quoteCurrency).__init__()

    def sell(self, date, asset, qty):
        return 0

    def buy(self, date, asset, qty):
        return 1


class Portfolio:
    pf: AbstractPortfolio

    def __init__(self, pf):
        return

    def f():
        return