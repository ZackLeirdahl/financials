from pyEX.client import  *
#c = Client('sk_c7bf589a15d04f3585c8313ea6c47d5b')
#print(c.calendar())
#
#

# import pytradier
from authorization import _tokens
# from pytradier.tradier import Tradier
# tradier = Tradier(token=_tokens['tradier'])
# # company = tradier.company('MSFT')
# # history = company.history(interval='daily', start='2019-1-1', end='2019-3-1')
# # print(history._data)
# stock = tradier.stock('BAC')
# print(stock.average_volume())

from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.timeseries import TimeSeries
ts =TimeSeries(key=_tokens['alphavantage'])
print(ts.get_intraday('SPLK'))
#sp = SectorPerformances(key=_tokens['alphavantage'])
#print(sp.get_sector())
#ti = TechIndicators(key=_tokens['alphavantage'],output_format='pandas')
#print(ti.get_rsi('SPLK'))
_endpoints = ["chart", "quote", "book", "open-close", "previous","company", "stats", "peers", "relevant", "news","financials", "earnings", "dividends", "splits", "logo", "price", "delayed-quote", "effective-spread", "volume-by-venue", "ohlc"]
