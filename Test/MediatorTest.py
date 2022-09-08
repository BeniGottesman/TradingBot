import Portfolio.Portfolio as pf
import Portfolio.Share as sh
import Strategy.JohanssenClassic as jo
import mediator as med
import enums as cst
import backtest as bt
import dataRetrieving as dr


def testStrategy () -> None :
    quoteCurrency = "USDT"
    portfolioName = "test portfolio"
    startingMoney = 1000.0
    myPF = pf.Portfolio(quoteCurrency, portfolioName, startingMoney)
    
    referencePair = 'BTCUSDT'
    checkCryptoVolume = {}
    checkCryptoVolume[quoteCurrency] = 250000000

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
    
    for key in data:
        myPF.add(sh.cryptoCurrency(key))
    
    print(myPF.getNumberOfShares())
    print(myPF)
    myPF.presentState()
    
    daysrollingwindow = 30
    timeCycleInSecond = 15*60
    initialInvestmentPercentage = 1
    transactionCost = 0.0015
    name="Test Strategy"
    
    JohannsenStrat = jo.JohannsenClassic(myPF, daysrollingwindow, timeCycleInSecond, initialInvestmentPercentage, transactionCost, name)
    #mediator = med.Trading (JohannsenStrat, myPF)
    
    c = 1.
    JohannsenStrat.doAlgorithm(myPF, c, data, False)