from stock import Stock
from iex import StockReader
<<<<<<< HEAD
from robinhood import Robinhood
from option import Option
=======
from option import Option
from robinhood import Robinhood
>>>>>>> a3fc165c3005ed352acdea0102006b50a2d44c48
import pandas as pd


#VWAP 1 Day = (Sum of number of shares bought * price) / number of shares bought
<<<<<<< HEAD
# s = StockReader(['NVDA'])
=======
# s = StockReader(['NFLX'])
>>>>>>> a3fc165c3005ed352acdea0102006b50a2d44c48
# chart = s.get_chart(range='1d')
# vw = 0
# volume = 0
# for point in chart:
#     avg = float(point['marketAverage'])
#     vol = float(point['marketVolume'])
#     vw += avg * vol
#     volume += vol
# vwap = vw/volume
<<<<<<< HEAD
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
=======
# print(vwap)
###########################

#Find highest_volume for option chain
r = Robinhood()
volume = 0
highest_volume = None
for option in r.get_options('NFLX',['2019-01-18','2019-01-25'],'call'):
    temp_vol = r.get_option_market_data(option['id'])['volume']
    if temp_vol > volume:
        volume = temp_vol
        highest_volume = option
###################################
>>>>>>> a3fc165c3005ed352acdea0102006b50a2d44c48
