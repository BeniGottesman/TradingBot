# from re import sub
# from typing import List
# import random 
# import time
import matplotlib.pyplot as plt
import numpy as np

import Strategy.strategy as strat
import designPattern.observer as obs
import Portfolio.portfolio as pf

class StatisticsViewer(obs.Observer):
    """
    This class display some statistics, graph ... about a strategy
    """
    def __init__(self) -> None:
        # self.__stat_data__ : List[dict] = []
        self.__stat_data__ : dict = {}
        self.__TCV__       : dict = {}
        self.__nb_stop_loss__  = 0
        self.__nb_short__      = 0
        self.__nb_long__       = 0
        self.__nb_freeze__     = 0
        self.__total__         = 0 # = __nb_long__+__nb_short__
        self.__long__   : list = []
        self.__short__  : list = []

    def update(self, subject: obs.Subject) -> None:
        """
        If called it means new datas has arrived.
        we store/add the datas inside __stat_data__.
        """
        # self.__stat_data__.append(_data)
        tmp_report = subject.get_report()
        for time_key, _ in tmp_report.items():
            if tmp_report[time_key]["Position Status"] == "Freeze":
                self.__nb_freeze__       += 1
            elif tmp_report[time_key]["Position Status"] == "Enter":
                if tmp_report[time_key]["Position"]   == "Long":
                    self.__nb_long__       += 1
                    self.__short__.append (0)
                    self.__long__.append  (1)
                elif tmp_report[time_key]["Position"] == "Short":
                    self.__nb_short__      += 1
                    self.__short__.append (1)
                    self.__long__.append  (0)
            elif tmp_report[time_key]["Position"] == "Stop Loss":
                self.__nb_stop_loss__  += 1
                self.__short__.append   (0)
                self.__long__.append    (0)
            else:
                self.__short__.append   (0)
                self.__long__.append    (0)
            self.__total__ = self.__nb_long__ + self.__nb_short__
            #Just keep once the TCV -> scale graph
            self.__TCV__[time_key] = tmp_report[time_key]["Portfolio"]["TCV"]
        self.__stat_data__.update(tmp_report) #equivalent to append for dictionnary

    def __str__(self)-> None:
        tmp_str  = ""
        tmp_str += "Number of Long Position = "  + str(self.__nb_long__)
        tmp_str += "\n"
        tmp_str += "Number of Short Position = " + str(self.__nb_short__)
        tmp_str += "\n"
        tmp_str += "Total = " + str(self.__total__)
        tmp_str += "\n"
        tmp_str += "Number of Stop Loss = "      + str(self.__nb_stop_loss__)
        tmp_str += "\n"
        tmp_str += "Number of Freeze = "      + str(self.__nb_freeze__)
        tmp_str += "\n"

        return tmp_str

    def plot_TCV (self) -> None:
        # tmp_report = self.__stat_data__
        # tmp_sym = symbol_to_trade[0]
        # x_axis = market.get_index(tmp_sym, 'Close Time', self.__rollingwindow__, end+1)
        x_axis = self.__TCV__.keys () # PROBLEM TO CORRECT THERE IS A LAG IN THE DATES
        #Just keep once the TCV -> scale graph
        y_axis = self.__TCV__.values ()
        plt.show(block=False)
        plt.clf()
        # markers_on_long = np.where (np.asarray(self.__long__) == 1) [0]
        # markers_on_short = np.where (np.asarray(self.__short__) == 1) [0]
        markers_on_entry_long  = [list(y_axis)[i]
                            if self.__long__[i]==1 else np.nan for i in range(len(self.__long__))]
        markers_on_entry_short = [list(y_axis)[i]
                            if self.__short__[i]==1 else np.nan for i in range(len(self.__short__))]
        plt.plot(x_axis, y_axis, color='green', label='TCV', linewidth=1)
        plt.scatter(x_axis, markers_on_entry_long,
                    marker='x', color='red', s=12, label='long')
        plt.scatter(x_axis, markers_on_entry_short,
                    marker='x', color='blue', s=12, label='short')
        # plt.plot(x_axis, markers_on_short,
        #         marker='x', mfc='blue', mec='blue', ms=2, label='short')

        plt.title("P&L")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.legend()

        plt.gcf().autofmt_xdate()
        # plt.pause(0.05)
        plt.show()


# References
# https://refactoring.guru/fr/design-patterns/observer/python/example
# https://stackoverflow.com/questions/8409095/set-markers-for-individual-points-on-a-line-in-matplotlib
