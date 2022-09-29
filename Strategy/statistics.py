from re import sub
from typing import List
import random 
import time

import strategy as strat
import designPattern.observer as obs
import Portfolio.portfolio as pf

class StatisticsViewer(obs.Observer):
    def __init__(self) -> None:
        # self.__stat_data__ : List[dict] = []
        self.__stat_data__ : dict = {}
        self.stop_loss = 0
        self.short = 0
        self.long = 0
        self.enter

    def update(self, subject: obs.Subject) -> None:
        """
        If called it means new datas has arrived.
        we store/add the datas inside __stat_data__.
        """
        # self.__stat_data__.append(_data)
        tmp_report = subject.report()
        if tmp_report["Position"] == "Long":
            self.long +=1
        elif tmp_report["Position"] == "Short":
            self.short +=1
        elif tmp_report["Position"] == "Stop Loss":
            self.stop_loss +=1
        self.__stat_data__.update(tmp_report) #equivalent to append for dictionnary



# References
# https://refactoring.guru/fr/design-patterns/observer/python/example
