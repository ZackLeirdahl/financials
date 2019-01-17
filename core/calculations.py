from stock import Stock
from iex import StockReader
from option import Option
from robinhood import Robinhood

def get_vwap_daily(ticker_symbol, vw = 0, volume = 0):
    s = StockReader([ticker_symbol])
    for point in s.get_chart(range='1d'):
        avg = float(point['marketAverage'])
        vol = float(point['marketVolume'])
        vw += avg * vol
        volume += vol
    return round(vw/volume,2)

def get_highest_volume(ticker_symbol, dates, type, volume = 0, highest_volume = None):
    r = Robinhood()
    for option in r.get_options(ticker_symbol, dates, type):
        temp_vol = r.get_option_market_data(option['id'])['volume']
        if temp_vol > volume:
            volume = temp_vol
            highest_volume = option
    return highest_volume
