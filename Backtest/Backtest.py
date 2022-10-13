from datetime import datetime
import Portfolio.portfolio as pf
import Portfolio.share as sh
import Strategy.johanssen_classic as jo
import mediator as med
import enums as cst
import binance_data.scrap_datas as bt
import binance_data.data_retrieving as dr
import binance_data.csv_to_data as cd
import market_quotation as mq


def test_strategy () -> None :
    quote_currency = "USDT"
    # portfolio_name = "test portfolio"
    # starting_money = 1000.0
    # my_portfolio = pf.Portfolio(quote_currency, portfolio_name, starting_money)

    # reference_pair = 'BTCUSDT'
    # Scrap w.r.t. the volume
    # check_crypto_volume = {}
    # check_crypto_volume[quote_currency] = 7500000000
    start_date = "2020-04"
    end_date = "2022-08"
    parameters_scrap = {"folder": cst.ROOT_DIR,
                   "years": cst.YEARS, "months": [1,2,3,4,5,6,7,8,9,10,11,12],
                   "trading_type": "spot", "intervals": ['15m'],
                   "startDate": start_date, "endDate": end_date,
                   "checksum": False}

    #Old test
    #do_i_scrap = False #Turn to true for scrapping market datas
    # symbols_scrapped = bt.scrap_datas(check_crypto_volume, parameters_scrap, do_i_scrap)
    #Scrap w.r.t. the volume

    #LUNCUSDT does not exists in the database, binance url is down
    # if "LUNCUSDT" in symbols_scrapped["USDT"] :
    #     symbols_scrapped["USDT"].remove("LUNCUSDT")
    # In the next version
    # delete from the list the pairs if the url does not respond

    #Another version with my selected pairs
    pairs_to_trade= {}
    pairs_to_trade [quote_currency] =\
        ["BTCUSDT", "BNBUSDT"]
        # ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "ADAUSDT", "LTCUSDT", "BNBUSDT", "TRXUSDT"]
    # pairs_to_trade [quote_currency] = ["BTCUSDT", "SOLUSDT"]
    parameters_scrap["symbols"] = pairs_to_trade
    dr.retrieve_historic_from_binance_datas (parameters_scrap)
    #Another version with my selected pairs

    #3rd I convert them into a dataframe
    print("To dataframe: Start")
    # pairs_to_trade = symbols_scrapped[quote_currency]
    pairs_to_trade = pairs_to_trade[quote_currency]
    start_date = start_date + "-01"
    end_date = end_date + "-31"
    market_quotations = cd.csv_to_dataframe_of_many_pairs(pairs_to_trade, 'spot', '15m',\
                                                          start_date, end_date)
    #We initialize the market quotation client
    mq.MarketQuotationClient (market_quotations)
    # test.get_client().set_quotations(market_quotations)
    print("To dataframe: Done.")

    print("Strategy: Start.")
    #Shares to trade
    _shares = []
    for key in market_quotations:
        _shares.append(key)

    #Parameters for johanssen Strategy
    time_candle = 15
    days_rolling_window = 300
    time_cycle_in_second = time_candle * 60
    initial_investment_percentage = 0.10
    transaction_cost = 0.0010000
    strategy_name = "Test Strategy"
    _days = 2
    _freezing_cycle = _days * (24*60/time_candle) #4 days freezing
    stop_loss_activated = False
    parameters_strategy = {
            "starting money": 1000,
            "portfolio name": "test Joahnsen portfolio",
            "quote currency": "USDT",
            "time candle": time_candle,
            "shares": _shares,
            "days rolling window": days_rolling_window,
            "time cycle in second": time_cycle_in_second,
            "initial investment percentage": initial_investment_percentage,
            "transaction cost": transaction_cost,
            "strategy name": strategy_name, "freezing cycle": _freezing_cycle,
            "stop loss activated": stop_loss_activated,
            "start date": datetime.strptime(start_date, '%Y-%M-%d'),
            "end date": end_date}
    johannsen_strategy = jo.JohannsenClassic(parameters_strategy)
    # number_of_quotations_periods = market.number_of_period()
    # johannsen_strategy = jo.JohannsenClassic(_shares,
    #                         days_rolling_window, time_cycle_in_second,
    #                         initial_investment_percentage, transaction_cost,
    #                         _freezing_cycle, stop_loss_activated,
    #                         start_date, end_date,
    #                         strategy_name)

    constant_std = 4.5
    johannsen_strategy.do_strategy(constant_std, pairs_to_trade, False)
    print("Strategy: Done.")
