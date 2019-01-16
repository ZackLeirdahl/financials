from stock import Stock
from iex import StockReader
from robinhood import Robinhood
from option import Option
import pandas as pd


#VWAP 1 Day = (Sum of number of shares bought * price) / number of shares bought
# s = StockReader(['NVDA'])
# chart = s.get_chart(range='1d')
# vw = 0
# volume = 0
# for point in chart:
#     avg = float(point['marketAverage'])
#     vol = float(point['marketVolume'])
#     vw += avg * vol
#     volume += vol
# vwap = vw/volume
#######################

#Get the option with the highest volume
r = Robinhood()
vol = 0
highest_vol = None
options = r.get_options('AMD', ['20190118','20190125','20190201','20190208','20190215'],'call')
for option in options:
    o = Option(option['url'])
    if o.volume > vol:
        vol = o.volume
        highest_vol = o
##########
