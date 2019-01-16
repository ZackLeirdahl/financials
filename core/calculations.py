from stock import Stock
from iex import StockReader
from robinhood import Robinhood
from option import Option

#VWAP 1 Day = (Sum of number of shares bought * price) / number of shares bought
# s = StockReader(['NFLX'])
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
