from binance.client import Client #, ThreadedWebsocketManager, ThreadedDepthCacheManager
from designPattern.Singleton import Singleton
import Keys as keys

#see https://algotrading101.com/learn/binance-python-api-guide/
#see https://testnet.binance.vision/

apikey = keys.API_Key
apisecret = keys.Secret_Key

class client(metaclass=Singleton):
    def __init__(self):
        self.cl = Client(apikey, apisecret)

    def getClient (self):
        return self.cl