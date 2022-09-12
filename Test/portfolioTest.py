import Portfolio.Portfolio as pf
import Portfolio.Share as sh

def test_portfolio () -> None :
    quote_currency = "USD"
    portfolio_name = "test portfolio"
    starting_money = 1000.0
    my_portfolio = pf.Portfolio(quote_currency, portfolio_name, starting_money)

    share_1 = sh.cryptoCurrency("BTCUSD")
    share_2 = sh.cryptoCurrency("ETHUSD")
    my_portfolio.add_share(share_1)
    my_portfolio.add_share(share_2)
    print(my_portfolio.get_number_of_shares())
    my_portfolio.remove_share(share_1)
    print(my_portfolio)
    print(my_portfolio.get_number_of_shares())
    print("value = ", my_portfolio.value())

    portfolio_report = my_portfolio.report()
    tmp = str(portfolio_report[share_2.get_name()]).strip("{}")
    print(tmp)

    my_portfolio.presentState()
    