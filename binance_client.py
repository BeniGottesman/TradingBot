from binance.client import Client #, ThreadedWebsocketManager, ThreadedDepthCacheManager
from designPattern.singleton import Singleton
import keys as keys

#see https://algotrading101.com/learn/binance-python-api-guide/
#see https://testnet.binance.vision/

apikey = keys.API_Key
apisecret = keys.Secret_Key

class client(metaclass=Singleton):
    def __init__(self):
        self.__client__ = Client(apikey, apisecret)

    def get_client (self):
        return self.__client__
    