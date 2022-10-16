import datetime
import sys
import numpy as np
import matplotlib.pyplot as plt
from time import time as tm

import Maths.statistics as statistics
import Strategy.strategy_state as state
import Strategy.strategy as st
import Portfolio.share as sh
import Portfolio.portfolio as pf
import Portfolio.portfolio_state as pfstate
import Strategy.statistics as stat
import market_quotation as mq

# market_quotations = mq.MarketQuotation()

class JohannsenClassic (st.Strategy):
    """
    JohannsenClassic is a class in which we apply the Johannsen strategy.
    """
    def __init__(self, parameters: dict):
        if  parameters["initial investment percentage"] > 1 or\
            parameters["initial investment percentage"] < 0:
            print('error JohannsenClassic: _initial_investment_percentage')
            sys.exit()
        #We create a new portfolio = 0 with the shares we will trade with
        initial_investment_percentage = parameters["initial investment percentage"]
        quote_currency = parameters['quote currency']
        portfolio_name = parameters['portfolio name']
        starting_money = parameters['starting money']
        my_portfolio = pf.Portfolio(quote_currency,
                                    portfolio_name, starting_money, initial_investment_percentage)
        for key in parameters['shares']:
            my_portfolio.add_share(sh.CryptoCurrency(key))
        #portfolio created
        #We call the super constructor
        super().__init__(my_portfolio, parameters['freezing cycle'],
                        parameters['initial investment percentage'],\
                        parameters['stop loss activated'],\
                        parameters['transaction cost'], parameters['start date'])
        self.__time_cycle_in_second__ = parameters['time cycle in second'] #15mn=15*60 for instance
        self.__time_candle__ = parameters['time candle']
        self.__rollingwindowindays__  = parameters['days rolling window'] #=30 days for instance
        self.__rollingwindow__        = int (\
            (60/(self.__time_cycle_in_second__/60))*24*self.__rollingwindowindays__)
        self.__name__ = parameters['strategy name']
        self.__start_date__ = parameters['start date']
        self.__end_date__   = parameters['end date']


    def johansen_weights_algorithm (self, time_now:datetime, moneys: list, quotations: np.array):
        time_serie_size   = quotations.shape[0]
        number_of_shares  = quotations.shape[1]
        log_return = np.zeros(shape=(time_serie_size, number_of_shares))

        # First we compute the spread
        for i in range (number_of_shares):
            col = np.array (statistics.log_Transform(quotations[:,i]))
            log_return [:,i] = col

        p_test = 1
        jres = statistics.get_johansen(log_return, p_test)

        spread_weights = jres.evecr[:,0] # Weights to hold in order to make the mean reverting strat
        #normalisation with the first crypto
        # spread_weights = spread_weights/spread_weights[0] 

        return spread_weights, log_return

    # c=0.75 -> mu +/- 0.75xsigma
    # quotation = value of the different money now
    def do_one_day (self, time_now: datetime,
                    constant_std: float, moneys: list, quotations: np.array,
                    verbose = False) -> None:
        time_serie_size   = quotations.shape[0]
        # number_of_shares  = quotations.shape[1]

        spread_weights, log_return = self.johansen_weights_algorithm (time_now, moneys, quotations)

        # Once I obtain the spread
        # I check the state of the pf
        # the state of the strategy
        strategy_state = self.get_state() #string overload
        if strategy_state == "Freeze":
            self._state.add_counter(time_now) #string overload
            if strategy_state == "Freeze":
                return

        my_portfolio = self.get_portfolio()
        pf_state = my_portfolio.get_state()
        if pf_state == "READY": #or # if pfState == pfstate.PortfolioIsReady():

            one_day = int (24*60/self.__time_candle__)
            _day = 2*one_day
            # The Spread or Portfolio to buy see research Spread
            # if strategy_state.elapsed_time_in_second (time_now) > 10*(24*60*60):
            #     _day = 20*one_day
            spread      = np.dot (log_return, -spread_weights) #WARNING MINUS
            mu_average  = np.mean(spread[-_day:]) # Mean
            sigma       = np.var (spread[-_day:]) # Variance
            sigma       = np.sqrt(sigma)

            my_invested_money = my_portfolio.get_BAL ()
            entry_transaction_cost =\
                self.entry_strategy_transaction_cost(time_now, my_invested_money)

            ##################
            ###### ENTRY ######
            if strategy_state == "WaitToEntry":
                # We normalize the weights with the present money
                # Amount of money in USDT I actually hold in my balance to trade
                my_money = my_invested_money - entry_transaction_cost
                if my_money>0:
                    _q = quotations[time_serie_size-1,:]
                    _x = my_invested_money/spread[-1]
                    qty_invested = 0.5
                    how_much_to_invest_weights = -qty_invested*_x * np.log(_q)/_q
                else:
                    print("WARNING : my_money<=0, exit()\n")
                    how_much_to_invest_weights = np.array ([-12345 for key in moneys])
                    sys.exit()
                    # return

                investment_dict={}

                for key, value in zip(moneys, how_much_to_invest_weights):
                    investment_dict[key] = value #WARNING

                #In order to hedge our position
                investment_dict["BTCUSDT"] = -investment_dict["BTCUSDT"]
                #In order to hedge our position

                # We start the Long strategy
                if spread[-1] < mu_average-constant_std*sigma:
                    if spread[-1] - spread[-2] < 0:
                    # key = list(investment_dict)[0]
                    # investment_dict [key] = +investment_dict [key]
                    # for key in list(investment_dict)[1:]:
                    #     investment_dict[key] = -investment_dict[key]
                        strategy_state.trailing_buy(time_now, investment_dict,\
                                                    entry_transaction_cost)
                        my_portfolio.set_transaction_time(time_now)# check if it is useful
                        self.change_state (state.StrategyWaitToExit(time_now, self))
                        self.update_report(time_now,"Long","Enter",\
                                            my_portfolio, entry_transaction_cost)
                    self.debug_strat(time_now, spread, mu_average, constant_std,\
                         sigma, "BUY LONG", entry_transaction_cost)
                # We start the Short strategy
                elif spread[-1] > mu_average+constant_std*sigma:
                    if spread[-1] - spread[-2] > 0:
                    #####Short = inverse the spread#####
                        key = list(investment_dict)[0]
                        investment_dict [key] = - (investment_dict [key])
                        for key in list(investment_dict)[1:]:
                            investment_dict[key] = - (investment_dict [key])
                    ######Short = inverse the spread#####
                        strategy_state.trailing_buy(time_now,\
                            investment_dict, entry_transaction_cost)
                        my_portfolio.set_transaction_time(time_now)
                        self.change_state (state.StrategyWaitToExit(time_now, self))
                        self.update_report(time_now, "Short", "Enter",\
                                           my_portfolio, entry_transaction_cost)
                        self.set_strategy_short (True)
                        self.debug_strat(time_now, spread, mu_average, constant_std,\
                                         sigma, "BUY SHORT", entry_transaction_cost)

            ##################
            ###### EXIT ######
            elif strategy_state == "WaitToExit":
                exit_transaction_cost = self.exit_strategy_transaction_cost(time_now)
                buying_value = self.get_last_buying_value()
                portfolio_value = my_portfolio.get_TCV()
                # We exit the Short strategy
                # if portfolio_value/buying_value > 1.05+0.0015 :
                if portfolio_value/buying_value > 1.0 + 2*self.__transaction_cost__\
                    or strategy_state.elapsed_time_in_second (time_now) > 30*(24*60*60):
                    if spread[-1] < mu_average and self.is_strategy_short():
                        # if spread[-1] - spread[-2] < 0:
                            strategy_state.trailing_sell(time_now, exit_transaction_cost)
                            self.change_state (state.StrategyWaitToEntry(time_now, self))
                            self.update_report(time_now,"Short","Exit", my_portfolio, exit_transaction_cost)
                            self.set_strategy_short (False)
                            self.debug_strat(time_now, spread, mu_average, constant_std, sigma,\
                                "SELL SHORT", exit_transaction_cost)

                    # We exit the long strategy
                    elif spread[-1] > mu_average and not self.is_strategy_short():
                        # if spread[-1] - spread[-2] > 0:
                            strategy_state.trailing_sell(time_now, exit_transaction_cost)
                            self.change_state (state.StrategyWaitToEntry(time_now, self))
                            self.update_report(time_now,"Long","Exit", my_portfolio, exit_transaction_cost)
                            self.debug_strat(time_now, spread, mu_average, constant_std, sigma,\
                                "SELL LONG", exit_transaction_cost)

                # If we stay more than x-days into a position then we stop-loss
                elif strategy_state.elapsed_time_in_second (time_now) > 30*(24*60*60):
                    self.exit(time_now, self.__transaction_cost__ )
                    self.change_state (\
                        state.StrategyFreeze(time_now, self, self._freezing_cycle))
                    print ("time_elapsed() : STOP LOSS = ", time_now)
                    self.plot_mean_reverting (spread, mu_average, constant_std, sigma)
                    self.update_report(time_now, "Stop Loss", "Exit",\
                                        my_portfolio, entry_transaction_cost)

                #Stop Loss at x%
                elif portfolio_value/buying_value < 0.95:
                    if self._stop_loss_activated:
                        self.exit(time_now, self.__transaction_cost__ )
                        self.change_state (\
                            state.StrategyFreeze(time_now, self, self._freezing_cycle))
                        print ("STOP LOSS = ", time_now)
                        self.update_report(time_now, "Stop Loss", "Exit",\
                                            my_portfolio, entry_transaction_cost)

                # We freeze if we exit without arbitrage
                # It means we have just sold the pf
                if self.get_state() == "WaitToEntry"\
                     and portfolio_value/buying_value < 0.95 + self.__transaction_cost__:
                    self.change_state (state.StrategyFreeze(time_now, self, self._freezing_cycle))
                    self.update_report(time_now, "Freeze", "Exit",\
                                    my_portfolio, entry_transaction_cost)
                    print("Freezing.")

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

    #Vectorization
    #quotations: pd.DataFrame ?
    def do_strategy(self, constant_std: float,
                    symbol_to_trade: list, verbose = False) -> None:
            # timeIndex = quotations[0].index
            # symbol_to_trade = list(symbol_to_trade.keys())
        if len (symbol_to_trade) <= 0 :
            print("No symbole to trade in your strategy.")
            return

        my_portfolio = self.get_portfolio()

        #We create a new portfolio = 0 with the shares we will trade with
        for key in symbol_to_trade:
            my_portfolio.add_share(sh.CryptoCurrency(key))

        market = mq.MarketQuotationClient().get_client()
        market_quotation = market.get_quotation()

        number_of_quotations_periods = market.number_of_period()
        if self.__rollingwindow__ >= number_of_quotations_periods:
            print("No training time period")
            return

        number_of_shares = my_portfolio.get_number_of_shares()
        nparray_quotations = np.zeros(shape=(self.__rollingwindow__, number_of_shares))

        one_month = int (30*24*60/self.__time_candle__)
        t_0 = tm() #1. We measure the time taken by the algorithm
        tmp_sym = symbol_to_trade[0]#it is the first symbol just to browse the df
        i=0
        while True:
            beginning = i
            end = self.__rollingwindow__ + i
            if end >= number_of_quotations_periods:
                t_1 = tm() #2. We measure the time taken by the algorithm
                print("time taken = ", t_1-t_0)
                print(my_portfolio)
                self.notify()
                self._statistics_viewer.plot_TCV()
                break
            my_shares = my_portfolio.get_shares()
            j=0
            for key in my_shares:
                #We take the transpose
                col = np.array (market_quotation [key]["Close"] [ beginning : end ]).T
                nparray_quotations [:,j] = col
                # q = np.concatenate ([q, col], axis=1)
                j+=1
            time_now = market.time(tmp_sym, 'Close Time', end)
            my_portfolio.update_portfolio(time_now)
            self.do_one_day (time_now,
                            constant_std, symbol_to_trade,
                            nparray_quotations, verbose)

            verbose = True
            if verbose and i%one_month==0 and i > 0:
                t_1 = tm() #2. We measure the time taken by the algorithm
                print("i=", i, "time taken =", t_1-t_0)
                self.notify()
                print (self._statistics_viewer)
                print (my_portfolio)
                if verbose and 12*one_month%i==0 and i>=12*one_month:
                    self._statistics_viewer.plot_TCV()

            i+=1

    _debug = False
    def debug_strat(self, time_now, spread,\
        mu_average, constant_std, sigma, sell_or_buy, transaction_cost):
        my_portfolio = self.get_portfolio()
        print("time = ", time_now, ",",\
                "TCV = ", round (my_portfolio.get_TCV(),4),",",\
                "BAL = ", round(my_portfolio.get_BAL(),4),",",\
                sell_or_buy, ", Transaction Fee = ", round(transaction_cost,4),\
                ", sigma = ", round(sigma,4), "mu = ", round(mu_average,4))
        if self._debug:
            self.plot_mean_reverting (spread, mu_average, constant_std, sigma)


    def plot_mean_reverting (self,\
                            spread, mu_average, constant_std, sigma):
        number_of_ticks = 96*2+10
        plt.show(block=False)
        plt.clf()
        plt.plot(spread[-number_of_ticks:])
        plt.plot((mu_average-constant_std*sigma)*np.ones(number_of_ticks))
        plt.plot((mu_average)*np.ones(number_of_ticks))
        plt.plot((mu_average+constant_std*sigma)*np.ones(number_of_ticks))
        plt.show()

# References
# Binance Fees calculator : https://www.binance.com/en/support/faq/e85d6e703b874674840122196b89780a
#(1) https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pandas-dataframe
#(2) https://stackoverflow.com/questions/18835077/selecting-from-multi-index-pandas
