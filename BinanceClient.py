from binance.client import Client #, ThreadedWebsocketManager, ThreadedDepthCacheManager
from designPattern.Singleton import Singleton
import Keys as keys

apikey = keys.apikey
apisecret = keys.apisecret

class client(metaclass=Singleton):
    def __init__(self):
        self.cl = Client(apikey, apisecret)

    def getClient (self):
        return self.cl