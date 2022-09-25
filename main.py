# import BinanceClient as bc
# from datetime import date
# import os
# import matplotlib.pyplot as plt

# import dataRetrieving as dr
# import enums as cst
# import numpy as np
# import pandas as pd
# import maths.Statistics as statistics
# import backtest as bt

# import Test.ScrapAndJohanssonTest as ScrapAndJohansson
# import Test.portfolioTest as pfTest
import Backtest.Backtest as bt

# clienSingletonInstance = bc.client()
# client = clienSingletonInstance.get_client()

def main ():
    """Main function"""
    bt.test_strategy()

main()
