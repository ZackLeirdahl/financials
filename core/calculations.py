from stock import Stock
from iex import StockReader
import pandas as pd


#VWAP 1 Day = (Sum of number of shares bought * price) / number of shares bought
s = StockReader(['NVDA'])
chart = s.get_chart(range='1d')
vw = 0
volume = 0
for point in chart:
    avg = float(point['marketAverage'])
    vol = float(point['marketVolume'])
    vw += avg * vol
    volume += vol
vwap = vw/volume
