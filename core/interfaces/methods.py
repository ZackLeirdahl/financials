import operator
import pandas as pd
import numpy as np
from api import StockReader
from utils import *
from math import *

class StockMethods(StockReader):
    def __init__(self, symbol=None, login = True, output_format='json', **kwargs):
        StockReader.__init__(self, symbol, login, output_format, **kwargs)

    def get_historical_volatility(self):
        data = pd.DataFrame(self.get_chart(range='1y'))
        log_return = np.log(data['close'] / data['close'].shift(1))
        return round(np.sqrt(log_return.apply(lambda x: (x-log_return.mean())**2).mean()) * np.sqrt(252),4)

    def get_moving_average(self, n):
        return round(list(pd.Series.rolling(pd.DataFrame(self.get_chart(range = '1y'))['close'], n).mean())[-1],2)

    def get_vwap_daily(self):
        data = {float(p['marketVolume']): float(p['marketAverage'])*float(p['marketVolume']) for p in self.get_chart(range='1d')}
        return round(sum(list(data.values()))/sum(list(data.keys())),2)

    def get_average_volume(self):
        return sum([record['volume'] for record in self.get_chart()[-10:]])/10

    def get_overview(self, format_price = True):
        data = {'Volume': self.get_volume(), 'Average Volume': self.get_average_volume(), 'Price': self.get_price()}
        if format_price: data.update(self.get_price_overview())
        else: data.update(self.get_price_overview_percentages())
        return data

    def get_price_overview(self):
        return {'VWAP': self.get_vwap_daily(), 'MA(10)': self.get_moving_average(10),'MA(20)': self.get_moving_average(20), 'MA(50)': self.get_moving_average(50), 'High': self.get_ohlc()['high'], 'Low': self.get_ohlc()['low']}

    def get_price_overview_percentages(self):
        price = self.get_price()
        return {k: round(100 * (price/v),2) for k,v in self.get_price_overview().items()}

    def get_highest_volume_strike(self, weeks, type = 'call'):
        mkt_data = self.get_option_market_data(sorted({option['id']:self.get_option_market_data(option['id'])['volume'] for option in self.get_options(weeks, type)}.items(),key=operator.itemgetter(1),reverse=True)[0][0])
        inst = self.get_url(mkt_data['instrument'])
        return {'Expiration': inst['expiration_date'], 'Strike': inst['strike_price'], 'Mark': mkt_data['mark_price'], 'Volume': mkt_data['volume'], 'Open Interest': mkt_data['open_interest']}

    def get_open_interest(self, weeks, type):
        return sum([int(self.get_option_market_data(option['id'])['open_interest']) for option in self.get_options(weeks,type)])

    def get_option_volume(self, weeks, type):
        return sum([int(self.get_option_market_data(option['id'])['volume']) for option in self.get_options(weeks,type)])

    def get_call_put_spread(self, weeks = 2):
        call = self.get_open_interest(weeks, 'call')
        put = self.get_open_interest(weeks, 'put')
        return call/(call + put)

    def get_rsi(self, n=14, fillna=False):
        diff = pd.DataFrame(self.get_chart())['close'].diff()
        which_dn = diff < 0
        up, dn = diff, diff*0
        up[which_dn], dn[which_dn] = 0, -up[which_dn]
        emaup = ema(up, n, fillna)
        emadn = ema(dn, n, fillna)
        rsi = 100 * emaup / (emaup + emadn)
        if fillna:
            rsi = rsi.replace([np.inf, -np.inf], np.nan).fillna(50)
        return rsi

    def get_macd(self, n_fast=12, n_slow=26, fillna=False):
        close = pd.DataFrame(self.get_chart(range='1y'))['close']
        emafast = ema(close, n_fast, fillna)
        emaslow = ema(close, n_slow, fillna)
        macd = emafast - emaslow
        if fillna:
            macd = macd.replace([np.inf, -np.inf], np.nan).fillna(0)
        return macd
