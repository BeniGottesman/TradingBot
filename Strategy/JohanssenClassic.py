import datetime
import sys
# from typing import List
import numpy as np
# import pandas as pd

import maths.Statistics as statistics
import Strategy.Strategystate as state
import Strategy.Strategy as st
import Portfolio.Share as sh
import Portfolio.portfolio as pf
import Portfolio.PfState as pfstate
import marketquotation as mq

# market_quotations = mq.MarketQuotation()

class JohannsenClassic (st.Strategy):
    """JohannsenClassic is a class in which we apply the Johannsen strategy."""
    def __init__(self, portfolio: pf.Portfolio,
                 _daysrollingwindow: int, _time_cycle_in_second: int,
                 _initial_investment_percentage : float, _transaction_cost: float, 
                 _name="generic strategy") -> None:
        self.__time_cycle_in_second__ = _time_cycle_in_second #15mn=15*60 for instance
        self.__rollingwindowindays__ = _daysrollingwindow #=30 days for instance
        self.__rollingwindow__ = int ((60/(self.__time_cycle_in_second__/60))*24*_daysrollingwindow)
        self.__transaction_cost__ = _transaction_cost
        self.__backtest__ = st.BacktestCommand(portfolio)
        if _initial_investment_percentage > 1 or _initial_investment_percentage < 0:
            sys.exit()
        #initial_investment_percentage=This variable is 1 i.e. not used yet
        #i.e. 0.2% of the capital for instance
        self.__initial_investment_percentage__ = _initial_investment_percentage
        self.__state__ = state.StrategyWaitToEntry()


    # c=0.75 -> mu +/- 0.75xsigma
    # quotation = value of the different money now
    def do_one_day (self, time_now: datetime,
                    portfolio: pf.Portfolio, portfolio_caretaker: pf.PortfolioCaretaker,
                    constant_std: float, moneys: list, quotations: np.array, 
                    verbose = False) -> None:
        time_serie_size   = quotations.shape[0]
        number_of_shares  = quotations.shape[1]
        log_return = np.zeros(shape=(time_serie_size, number_of_shares))

        market_quotation = mq.MarketQuotationClient().get_client().get_quotation()

        # First we compute the spread
        for i in range (number_of_shares):
            # log_return[key] =
            # np.array (stat.log_Transform(quotations[key]["Close"][beginningWindow:endWindow]))
            col = np.array (statistics.log_Transform(quotations[:,i]))
            log_return [:,i] = col

        # pd_lr_price_series =
        # pd.DataFrame(index=quotations['Close Time'],
        # data={key: log_return[key] for key in log_return})
        # pd_lr_price_series =
        # pd_lr_price_series[-self.__rollingwindow__:]#we take only the last 30 days
        p_test = 1
        #log_return=pd.DataFrame(data={key: log_return[key] for key in log_return})
        jres = statistics.get_johansen(log_return, p_test)

        # if verbose :
        #     print ("There are", jres.r, "cointegration vectors")

        # v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
        spread_weights = jres.evecr[:,0] # Weights to hold in order to make the mean reverting strat
        spread_weights = spread_weights/spread_weights[0] #normalisation with the first crypto

        # Once I obtain the spread
        # I check the state of the pf
        error = 0.5
        #the state of the strategy
        present_strategy_state = self.__state__.get_state() #string overload
        my_money = portfolio.get_BAL ()# Amount of money I  actually hold in my pf

        pf_state = portfolio.getState()
        if pf_state == "READY": #or # if pfState == pfstate.PortfolioIsReady():
            spread = spread_weights * quotations[time_serie_size-1,:] #= value
            alpha=1
            if my_money>0:
                alpha  = spread/my_money
            how_much_to_invest_weights = spread_weights/alpha
            #Next line To delete ?
            how_much_to_invest_weights = how_much_to_invest_weights/number_of_shares

            mu_average  = np.mean (np.dot(log_return, how_much_to_invest_weights)) # Mean
            sigma       = np.var (np.dot(log_return, how_much_to_invest_weights)) # Variance
            sigma       = np.sqrt(sigma)
            # The Spread or Portfolio to buy see research Spread
            spread      = np.dot (log_return, how_much_to_invest_weights) 

            investment_dict={}
            quotation_dict={}
            i=0
            for key, value in zip(moneys, how_much_to_invest_weights):
                investment_dict[key] = value
                quotation_dict[key] = quotations[-1,i]
                i+=1
            #  portfolio.updateMarketQuotation(time_now, quotation_dict)

            if present_strategy_state == "WaitToEntry":
                #if the last value of the mean reverting serie=spread[-1]<... then

                #we start the Long strategy
                if spread[-1] < mu_average-constant_std*sigma and\
                    spread[-1] - spread[-2] < 0:
                    key = list(investment_dict)[0]
                    investment_dict [key] = +investment_dict [key]
                    for key in list(investment_dict)[1:]:
                        investment_dict[key] = -investment_dict[key]
                    self.__backtest__.entry(time_now, investment_dict)
                    # portfolio_value = portfolio.get_TCV()
                    portfolio.set_transaction_time(time_now)
                    portfolio_caretaker.backup(time_now)
                    self.__state__ = state.StrategyWaitToExit()
                    # print (self.__state__)
                 #we start the Short strategy
                if spread[-1] > mu_average+constant_std*sigma and\
                    spread[-1] - spread[-2] > 0:
                     # or -howMuchToInvestWeights ?
                    key = list(investment_dict)[0]
                    investment_dict [key] = -abs (investment_dict [key])
                    # for key in list(investment_dict)[1:]:
                    #     investment_dict[key] = +investment_dict[key]
                    self.__backtest__.entry(time_now, investment_dict)
                    # portfolio_value = portfolio.get_TCV()
                    portfolio.set_transaction_time(time_now)
                    portfolio_caretaker.backup(time_now)
                    self.__state__ = state.StrategyWaitToExit()
                    # print (self.__state__)
            elif present_strategy_state == "WaitToExit":
                buying_value = portfolio_caretaker.get_last_buying_value()
                portfolio_value = portfolio.get_TCV()
                balance = portfolio.get_BAL()
                # if (portfolio_value-balance)/(buying_value-balance) > 1.002+0.0015 :
                 #we exit the Short strategy
                if (portfolio_value)/(buying_value) > 1.00+0.0015 :
                    if spread[-1] < mu_average-constant_std*sigma and\
                        spread[-1] - spread[-2] > 0:
                        self.__backtest__.exit(time_now)
                        self.__state__ = state.StrategyWaitToEntry()
                    #we exit the long strategy
                    if spread[-1] > mu_average+constant_std*sigma and\
                        spread[-1] - spread[-2] < 0:
                        self.__backtest__.exit(time_now)
                        self.__state__ = state.StrategyWaitToEntry()

                #Stop Loss at 5%
                if portfolio_value*1./buying_value < 0.95:
                    self.__backtest__.exit(time_now)
                    self.__state__ = state.StrategyWaitToEntry()
                    print ("STOP LOSS")

            # self.__state__.setState("Nothing")
            #####Hedging : If we want to buy the spread#####
            #####Add this update in a new version#####
            ##### elif howMuchToInvestWeights-weightArrayOfShares > error: 
            # -> Not true, substraction of 2 arrays
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
    def do_algorithm(self, my_portfolio: pf.Portfolio, constant_std: float,
                    symbol_to_trade: list, verbose = False) -> None:
            # timeIndex = quotations[0].index
            # symbol_to_trade = list(symbol_to_trade.keys())
        if len (symbol_to_trade) <= 0 :
            print("No symbole to trade in your strategy.")
            return

        #We create a new portfolio = 0 with the shares we will trade with
        for key in symbol_to_trade:
            my_portfolio.add_share(sh.CryptoCurrency(key))

        market_quotation = mq.MarketQuotationClient().get_client().get_quotation()
        #see (1)
        # number_of_quotations_periods = len(symbol_to_trade[symbol_to_trade[0]]["Close"])
        # number_of_quotations_periods = number of rows
        number_of_quotations_periods = len(market_quotation[symbol_to_trade[0]])
        # number_of_quotations_periods = market_quotation.shape[0]
        # print("size=",market_quotation)

        portfolio_caretaker = pf.PortfolioCaretaker(my_portfolio)
        number_of_shares = my_portfolio.get_number_of_shares()
        nparray_quotations = np.zeros(shape=(self.__rollingwindow__, number_of_shares))
        i=0
        while True:
            beginning = i
            end = self.__rollingwindow__ + i
            if end >= number_of_quotations_periods:
                break
            my_shares = my_portfolio.get_shares()
            j=0
            for key in my_shares:
                #We take the transpose
                col = np.array (market_quotation [key]["Close"] [ beginning : end ]).T
                nparray_quotations [:,j] = col
                # q = np.concatenate ([q, col], axis=1)
                j+=1
            #index.get_level_values, see (2): Selecting from multi-index pandas
            time_now =\
                    market_quotation[symbol_to_trade[0]][ beginning : end ].index.get_level_values('Close Time')[-1]
#list (market_quotation[symbol_to_trade[0]]["Close Time"][ beginning : end ])[-1]
# list (market_quotation[symbol_to_trade[0]].iloc[market_quotation.index.get_level_values('Close Time') == 1]["Close Time"][ beginning : end ])[-1]
            my_portfolio.update_portfolio(time_now)
            self.do_one_day (time_now, my_portfolio, portfolio_caretaker,
                            constant_std, symbol_to_trade,
                            nparray_quotations, verbose)

            verbose = True
            if verbose and i%100==0:
                print("i =",i)
                print(my_portfolio)

            i+=1
        #portfolio.plot()

# References
# Binance Fees calculator : https://www.binance.com/en/support/faq/e85d6e703b874674840122196b89780a
#(1) https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pandas-dataframe
#(2) https://stackoverflow.com/questions/18835077/selecting-from-multi-index-pandas
