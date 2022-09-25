import binance_client as bc
import binance_data.data_retrieving as dr
import enums as cst
import maths.statistics as statistics

clientSingletonInstance = bc.client()
client = clientSingletonInstance.get_client()

def scrap_datas (check_crypto_volume: dict, parameters_scrap: dict, scrap=False)-> dict:
    """
    CheckCryptoVolume is a dict that contains
    the crypto and the 24h-volume minimum to download
    if scrap is True, then we scrap the datas w.r.t. retrieve_historic_from_binance_datas
    and parameters_scrap contains every parameters for scrapping
    """

    #1st we check the market with high exchange volume
    symbols_scrapped = get_pairs_volume(**check_crypto_volume)
    print(symbols_scrapped)

    #2nd I scrap the datas with the desired 24h-volume
    parameters_scrap["symbols"]=symbols_scrapped
    if scrap:
        dr.retrieve_historic_from_binance_datas (parameters_scrap)

    return symbols_scrapped


def get_pairs_volume(**asset)-> dict:
    """
    **asset is dict of key base currency
    and value is the minimal volume
    i.e. checkCryptoVolume['BTC']  = 100,
    and return every pairs XXXBTC such that the volume is over 100 last 24h
    """

    # import symbols from exchange infos
    symbols = {}
    for symbol in client.get_exchange_info()['symbols']:
        if symbol['isSpotTradingAllowed'] is True:
            symbols [symbol['symbol']] = symbol

    # get through the 24h tickers and add quote_volume
    for ticker in client.get_ticker():
        if ticker['symbol'] in symbols: #i.e. isSpotTradingAllowed
            #we add a quoteVolume key to the dictionnary
            symbols[ticker['symbol']]['quoteVolume'] = ticker['quoteVolume']

    dic_symbols = {}
    #LTCBTC = LTC = Base Asset, BTC = Quote Asset
    for quote_asset, _ in asset.items():#qA=Quote Asset
        dic_symbols[quote_asset] = 0
        pair = [] #exemple BTCUSDT
        for __, item in symbols.items():
            base_assets = item['baseAsset']
            if float(item['quoteVolume'])> float(asset[quote_asset])\
                and item['quoteAsset']==quote_asset:
                pair.append(base_assets+quote_asset)
        dic_symbols[quote_asset] = pair
        print(quote_asset,':', len(dic_symbols[quote_asset]))

    return dic_symbols
