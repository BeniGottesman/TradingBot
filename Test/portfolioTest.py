import Portfolio.Portfolio as pf
import Portfolio.Share as sh

def testPortfolio () -> None :
    quoteCurrency = "USD"
    portfolioName = "test portfolio"
    startingMoney = 1000.0
    myPF = pf.Portfolio(quoteCurrency, portfolioName, startingMoney)
    
    s1 = sh.cryptoCurrency("BTCUSD")
    s2 = sh.cryptoCurrency("ETHUSD")
    myPF.add_share(s1)
    myPF.add_share(s2)
    print(myPF.get_number_of_shares())
    myPF.remove_share(s1)
    print(myPF)
    print(myPF.get_number_of_shares())
    print("value = ", myPF.value())
    
    dict = myPF.report()
    x = str(dict[s2.get_name()]).strip("{}")
    print(x)
    
    myPF.presentState()