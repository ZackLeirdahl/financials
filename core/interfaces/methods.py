from api import StockReader
import pandas as pd
from utils import *
import operator

class StockMethods(StockReader):
    def __init__(self, symbol=None, login = True, output_format='json', **kwargs):
        StockReader.__init__(self, symbol, login, output_format, **kwargs)

    def get_historical_volatility(self, **kwargs):
        import numpy as np
        data = pd.DataFrame(self.get_chart(range='1y'))
        log_return = np.log(data['close'] / data['close'].shift(1))
        return round(np.sqrt(log_return.apply(lambda x: (x-log_return.mean())**2).mean()) * np.sqrt(252),4)

    def get_moving_average(self, n):
        return round(list(pd.Series.rolling(pd.DataFrame(self.get_chart(range = '1y'))['close'], n).mean())[-1],2)

    def get_vwap_daily(self, vw = 0, volume = 0):
        for point in self.get_chart(range='1d'):
            avg = float(point['marketAverage'])
            vol = float(point['marketVolume'])
            vw += avg * vol
            volume += vol
        return round(vw/volume,2)

    def get_average_volume(self, volume = 0):
        chart = self.get_chart()
        records = chart[len(chart)-10:]
        for record in records:
            volume +=record['volume']
        return volume/10

    def get_overview(self):
        ohlc = self.get_ohlc()
        return {'Volume': self.get_volume(), 'Average Volume': self.get_average_volume(), 'VWAP': self.get_vwap_daily(), 'MA(10)': self.get_moving_average(10),'MA(50)': self.get_moving_average(50), 'MA(200)': self.get_moving_average(200), 'High': ohlc['high'], 'Low': ohlc['low'], 'Open':ohlc['open']['price'], 'Close': ohlc['close']['price'], 'Price': self.get_price()  }

    def get_highest_volume_strike(self, weeks, type = 'call'):
        records = {option['id']:self.get_option_market_data(option['id'])['volume'] for option in self.get_options(weeks, type)}
        data = sorted(records.items(), key=operator.itemgetter(1),reverse=True)[0]
        mkt_data = self.get_option_market_data(data[0])
        inst = self.get_url(mkt_data['instrument'])
        return {'Expiration': inst['expiration_date'], 'Strike': inst['strike_price'], 'Mark': mkt_data['mark_price'], 'Volume': mkt_data['volume'], 'Open Interest': mkt_data['open_interest']}

x = StockMethods(['bac'])
print(x.get_highest_volume_strike('bac',2,'call'))
