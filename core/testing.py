from robinhood import Robinhood
from iex import StockReader
stocks = ['BAC','AMD','MSFT','FB','PYPL','SONO','GOOS']
for s in stocks:
    sr = StockReader([s])
    print(s + '\n' + str(sr.get_vwap_daily()))
