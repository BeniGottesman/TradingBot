import BinanceClient as bc
from datetime import date
import os
import dataRetrieving as dr
import enums as cst
import numpy as np
import pandas as pd
import maths.Statistics as stat
import backtest as bt
import matplotlib.pyplot as plt

import Test.ScrapAndJohanssonTest as ScrapAndJohansson
import Test.portfolioTest as pfTest
import Test.MediatorTest as medTest

clienSingletonInstance = bc.client()
client = clienSingletonInstance.getClient()

def main ():
    medTest.testStrategy()

main()