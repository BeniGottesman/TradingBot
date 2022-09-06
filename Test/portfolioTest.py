import Portfolio.Portfolio as pf
import Portfolio.Share as sh

def testPortfolio () -> None :
    quoteCurrency = "USD"
    portfolioName = "test portfolio"
    startingMoney = 1000.0
    myPF = pf.Portfolio(quoteCurrency, portfolioName, startingMoney)
    
    s1 = sh.cryptoCurrency("BTCUSD")
    s2 = sh.cryptoCurrency("ETHUSD")
    myPF.add(s1)
    myPF.add(s2)
    print(myPF.getNumberOfShares())
    myPF.remove(s1)
    print(myPF)
    print(myPF.getNumberOfShares())
    print("value = ", myPF.value())
    
    dict = myPF.report()
    x = str(dict[s2.getName()]).strip("{}")
    print(x)
    
    myPF.presentState()