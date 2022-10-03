import datetime
import sys
import numpy as np
import matplotlib.pyplot as plt
from time import time

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
    def __init__(self, portfolio: pf.Portfolio,
                 _daysrollingwindow: int, _time_cycle_in_second: int,
                 _initial_investment_percentage : float, _transaction_cost: float,
                 _freezing_cycle: int, start_date: str, end_date: str,
                 _name="generic strategy") -> None:
        super().__init__()
        self.__time_cycle_in_second__ = _time_cycle_in_second #15mn=15*60 for instance
        self.__rollingwindowindays__ = _daysrollingwindow #=30 days for instance
        self.__rollingwindow__ = int ((60/(self.__time_cycle_in_second__/60))*24*_daysrollingwindow)
        self.__transaction_cost__ = _transaction_cost
        self.__backtest__ = st.BacktestCommand(portfolio)
        if _initial_investment_percentage > 1 or _initial_investment_percentage < 0:
            print('error JohannsenClassic: _initial_investment_percentage')
            sys.exit()
        #initial_investment_percentage=This variable is 1 i.e. not used yet
        #i.e. 0.2% of the capital for instance
        self.__initial_investment_percentage__ = _initial_investment_percentage
        self.__state__ = state.StrategyWaitToEntry()
        self.__short_strategy__ = False
        self.__freezing_cycle__ = _freezing_cycle
        #Observers
        self._statistics_viewer = stat.StatisticsViewer()
        self.__start_day__  = start_date #useless
        self.__end_day__    = end_date #useless
        self.attach (self._statistics_viewer)#don't forget to remove it at the end

    # c=0.75 -> mu +/- 0.75xsigma
    # quotation = value of the different money now
    def do_one_day (self, time_now: datetime,
                    portfolio: pf.Portfolio, portfolio_caretaker: pf.PortfolioCaretaker,
                    constant_std: float, moneys: list, quotations: np.array,
                    verbose = False) -> None:
        time_serie_size   = quotations.shape[0]
        number_of_shares  = quotations.shape[1]
        log_return = np.zeros(shape=(time_serie_size, number_of_shares))

        # First we compute the spread
        for i in range (number_of_shares):
            col = np.array (statistics.log_Transform(quotations[:,i]))
            log_return [:,i] = col

        p_test = 1
        jres = statistics.get_johansen(log_return, p_test)

        # if verbose :
        #     print ("There are", jres.r, "cointegration vectors")
        #     input("Press Enter to continue...")

        # v =  np.array ([np.ones(jres.r), jres.evecr[:,0], jres.evecr[:,1]], dtype=object)
        spread_weights = jres.evecr[:,0] # Weights to hold in order to make the mean reverting strat
        spread_weights = spread_weights/spread_weights[0] #normalisation with the first crypto

        #since the spread is wrt the log so we add this loop
        market_quotation = mq.MarketQuotationClient().get_client()
        for i, _ in enumerate(spread_weights):
            _share_name = moneys[i]
            tmp_mq = market_quotation.\
                quotation('Close Time', _share_name, time_now)
            spread_weights [i] = spread_weights [i]*np.log(tmp_mq)/tmp_mq

        # Once I obtain the spread
        # I check the state of the pf
        # the state of the strategy
        present_strategy_state = self.__state__.get_state() #string overload
        if present_strategy_state == "Freeze":
            present_strategy_state = self.__state__.add_counter().get_state() #string overload
            if present_strategy_state == "Freeze":
                return
            self.__state__ = state.StrategyWaitToEntry()

        pf_state = portfolio.getState()
        if pf_state == "READY": #or # if pfState == pfstate.PortfolioIsReady():

            # The Spread or Portfolio to buy see research Spread
            spread      = np.dot (log_return, spread_weights)
            mu_average  = np.mean(spread) # Mean
            sigma       = np.var (spread) # Variance
            sigma       = np.sqrt(sigma)

            # plt.plot(spread[-30:])
            # plt.plot((mu_average-constant_std*sigma)*np.ones(30))
            # plt.plot((mu_average)*np.ones(30))
            # plt.plot((mu_average+constant_std*sigma)*np.ones(30))
            # plt.show()

            stop_loss_activated = True
            if present_strategy_state == "WaitToEntry":
                alpha=1
                my_money = portfolio.get_BAL ()# Amount of money in USDT I  actually hold in my pf
                if my_money>0:
                    alpha  = (spread_weights * quotations[time_serie_size-1,:]) / my_money
                    how_much_to_invest_weights = spread_weights/alpha
                    how_much_to_invest_weights = how_much_to_invest_weights/number_of_shares
                else:
                    print("WARNING : my_money<=0\n")
                    how_much_to_invest_weights = np.array ([-1234 for key in moneys])

                investment_dict={}

                for key, value in zip(moneys, how_much_to_invest_weights):
                    investment_dict[key] = value #WARNING

                # plt.plot (spread)
                # plt.plot ((mu_average-constant_std*sigma)*np.ones(len(spread) ))
                # plt.plot ((mu_average+constant_std*sigma)*np.ones(len(spread) ))
                # plt.show()

                #we start the Long strategy
                if spread[-1] < mu_average-constant_std*sigma:
                    # if spread[-1] - spread[-2] > 0:
                    # key = list(investment_dict)[0]
                    # investment_dict [key] = +investment_dict [key]
                    # for key in list(investment_dict)[1:]:
                    #     investment_dict[key] = -investment_dict[key]
                        self.__backtest__.entry(time_now, investment_dict)
                        portfolio.set_transaction_time(time_now)
                        portfolio_caretaker.backup(time_now)
                        self.__state__ = state.StrategyWaitToExit()
                        self.update_report(time_now,"Long","Enter", portfolio)
                 #we start the Short strategy
                elif spread[-1] > mu_average+constant_std*sigma:
                    # if spread[-1] - spread[-2] < 0:
                    #####Short = inverse the spread#####
                        key = list(investment_dict)[0]
                        investment_dict [key] = - (investment_dict [key])
                        for key in list(investment_dict)[1:]:
                            investment_dict[key] = - (investment_dict [key])
                    ######Short = inverse the spread#####
                        self.__backtest__.entry(time_now, investment_dict)
                        portfolio.set_transaction_time(time_now)
                        portfolio_caretaker.backup(time_now)
                        self.__state__ = state.StrategyWaitToExit()
                        self.update_report(time_now,"Short","Enter", portfolio)
                        self.__short_strategy__ = True
            elif present_strategy_state == "WaitToExit":
                buying_value = portfolio_caretaker.get_last_buying_value()
                portfolio_value = portfolio.get_TCV()
                # We exit the Short strategy
                # if portfolio_value/buying_value > 1.05+0.0015 :
                if spread[-1] < mu_average:#-constant_std*sigma and self.__short_strategy__:
                # if spread[-1] < mu_average and self.__short_strategy__:
                    # if spread[-1] - spread[-2] < 0:
                        self.__backtest__.exit(time_now)
                        self.__state__ = state.StrategyWaitToEntry()
                        self.update_report(time_now,"Short","Exit", portfolio)
                        self.__short_strategy__ = False

                # We exit the long strategy
                elif spread[-1] > mu_average:#+constant_std*sigma and not self.__short_strategy__:
                # elif spread[-1] > mu_average and not self.__short_strategy__:
                    # if spread[-1] - spread[-2] > 0:
                        self.__backtest__.exit(time_now)
                        self.__state__ = state.StrategyWaitToEntry()
                        self.update_report(time_now,"Long","Exit", portfolio)

                #Stop Loss at 5%
                elif portfolio_value/buying_value < 0.95:
                    if stop_loss_activated:
                        self.__backtest__.exit(time_now)
                        self.__state__ = state.StrategyFreeze(self.__freezing_cycle__)
                        print ("STOP LOSS = ",time_now)
                        self.update_report(time_now,"Stop Loss","Exit", portfolio)

                #We freeze if we exit without arbitrage
                if self.__state__.get_state() == "WaitToEntry"\
                     and portfolio_value/buying_value < 1.0015:
                    self.__state__ = state.StrategyFreeze(self.__freezing_cycle__)

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
    def do_strategy(self, my_portfolio: pf.Portfolio, constant_std: float,
                    symbol_to_trade: list, verbose = False) -> None:
            # timeIndex = quotations[0].index
            # symbol_to_trade = list(symbol_to_trade.keys())
        if len (symbol_to_trade) <= 0 :
            print("No symbole to trade in your strategy.")
            return

        #We create a new portfolio = 0 with the shares we will trade with
        for key in symbol_to_trade:
            my_portfolio.add_share(sh.CryptoCurrency(key))

        market = mq.MarketQuotationClient().get_client()
        market_quotation = market.get_quotation()

        number_of_quotations_periods = market.number_of_period()
        if self.__rollingwindow__ >= number_of_quotations_periods:
            print("No training time period")
            return

        portfolio_caretaker = pf.PortfolioCaretaker(my_portfolio)
        number_of_shares = my_portfolio.get_number_of_shares()
        nparray_quotations = np.zeros(shape=(self.__rollingwindow__, number_of_shares))

        t_0 = time() #1. We measure the time taken by the algorithm
        tmp_sym = symbol_to_trade[0]#it is the first symbol just to browse the df
        i=0
        while True:
            beginning = i
            end = self.__rollingwindow__ + i
            if end >= number_of_quotations_periods:
                t_1 = time() #2. We measure the time taken by the algorithm
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
            self.do_one_day (time_now, my_portfolio, portfolio_caretaker,
                            constant_std, symbol_to_trade,
                            nparray_quotations, verbose)

            verbose = True
            if verbose and i%500==0 and i > 0:
                t_1 = time() #2. We measure the time taken by the algorithm
                print("i=", i, "time taken =", t_1-t_0)
                self.notify()
                print (self._statistics_viewer)
                print (my_portfolio)
                if verbose and i%10000==0:
                    self._statistics_viewer.plot_TCV()

            i+=1



# References
# Binance Fees calculator : https://www.binance.com/en/support/faq/e85d6e703b874674840122196b89780a
#(1) https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pandas-dataframe
#(2) https://stackoverflow.com/questions/18835077/selecting-from-multi-index-pandas
