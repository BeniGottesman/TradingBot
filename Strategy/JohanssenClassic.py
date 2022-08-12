import Strategy
import Portfolio.Portfolio as pf 

class JohannsenClassic(Strategy):
    def doAlgorithm(self, pf: pf.AbstractPortfolio, data: List) -> List:
        #writte algo
        return 1