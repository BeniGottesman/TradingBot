import Portfolio.Portfolio as pf
import Portfolio.Share as sh
import Strategy.JohanssenClassic as jo
import mediator as med
import enums as cst
import backtest as bt
import dataRetrieving as dr
import MarketQuotation as mq


def test_strategy () -> None :
    quote_currency = "USDT"
    portfolio_name = "test portfolio"
    starting_money = 1000.0
    my_portfolio = pf.Portfolio(quote_currency, portfolio_name, starting_money)

    # reference_pair = 'BTCUSDT'
    check_crypto_volume = {}
    check_crypto_volume[quote_currency] = 250000000

    #f = os.path.dirname(os.path.realpath(__file__))+"\\"
    parameters_scrap = {"folder": cst.ROOT_DIR,
                  "years": cst.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                  "trading_type": "spot", "intervals": ['15m'],
                  "startDate": "2017-01", "endDate": "2022-08",
                  "checksum": False}
    do_i_scrap = False #Turn to true for scrapping market datas
    symbols_scrapped = bt.scrapDatas(check_crypto_volume, parameters_scrap, do_i_scrap)

    #3rd I convert them into a dataframe
    print("To dataframe")
    pairs_to_trade = symbols_scrapped[quote_currency]
    market_quotations = dr.csv_to_dataframe_of_many_pairs(pairs_to_trade, 'spot', '15m')
    #We initialize the market quotation client
    mq.MarketQuotationClient (market_quotations)
    # test.get_client().set_quotations(market_quotations)
    print("To dataframe: Done.")

    #We create a new portfolio = 0 with the shares we will trade with
    for key in market_quotations:
        my_portfolio.add_share(sh.cryptoCurrency(key))

    #Portfolio Response test
    # print(my_portfolio.get_number_of_shares())
    # print(my_portfolio)
    # my_portfolio.presentState()

    #Parameters for johanssen Strategy
    days_rolling_window = 30
    time_cycle_in_second = 15*60
    initial_investment_percentage = 1
    transaction_cost = 0.0015
    strategy_name = "Test Strategy"

    johannsen_strategy = jo.JohannsenClassic(my_portfolio,
                            days_rolling_window, time_cycle_in_second,
                            initial_investment_percentage, transaction_cost, strategy_name)
    #mediator = med.Trading (JohannsenStrat, myPF)

    constant_std = 1.
    johannsen_strategy.do_algorithm(my_portfolio, constant_std, pairs_to_trade, False)
