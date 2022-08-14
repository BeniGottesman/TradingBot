# https://refactoring.guru/fr/design-patterns/observer/python/example
import Portfolio
from typing import List
import random 
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import designPattern.observer as obs
import Portfolio.Portfolio as pf

class TransactionsViewer(obs.Observer):
    def __init__(self) -> None:
        self.__transaction__ : List[dict] = []

    def update(self, subject: pf.AbstractPortfolio) -> None:
        self.__transaction__.append(subject.report())

class GraphTCVViewer(obs.Observer):
    def __init__(self) -> None:
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1,1,1)
        self.ax2 = self.fig.add_subplot(1,1,1)
        self.xs = []
        self.TCV = []
        self.BAL = []
        self.line, = self.ax1.plot(self.xs, self.TCV)
        self.line, = self.ax2.plot(self.xs, self.BAL)
        plt.xlabel('Time')
        plt.ylabel('TCV')
        plt.title('TCV Graph')

    def update(self, subject: pf.AbstractPortfolio) -> None:
        report = subject.report()
        self.xs.append (report["time"]) #time
        self.TCV.append (report["BAL"])
        self.BAL.append (report["TCV"])

    def plot(self) -> None:
        plt.plot(self.xs, self.TCV)
        plt.gcf().autofmt_xdate()
        plt.show()