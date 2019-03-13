import operator
import pandas as pd
import numpy as np
from client import Client
from utils import *
from math import *

class ClientMethods(Client):
    def __init__(self, symbol=None, **kwargs):
        Client.__init__(self, symbol, **kwargs)

    def get_historical_volatility(self):
        data = pd.DataFrame(self.get_chart(range='1y'))
        log_return = np.log(data['close'] / data['close'].shift(1))
        return round(np.sqrt(log_return.apply(lambda x: (x-log_return.mean())**2).mean()) * np.sqrt(252),4)

    def get_vwap_daily(self):
        data = {float(p['marketVolume']): float(p['marketAverage'])*float(p['marketVolume']) for p in self.get_chart(range='1d')}
        return round(sum(list(data.values()))/sum(list(data.keys())),2)

    def get_average_volume(self):
        return sum([record['volume'] for record in self.get_chart()[-10:]])/10

    def get_overview(self, format_price = True):
        data = self.get_misc_overview()
        data.update(self.get_price_overview(format_price))
        return data

    def get_misc_overview(self):
        return {'Volume': self.get_volume(), 'Average Volume': self.get_average_volume(), 'Price': self.get_price()}

    def get_price_overview(self, format_price = True):
        data = {'VWAP': self.get_vwap_daily(), 'High': self.get_ohlc()['high'], 'Low': self.get_ohlc()['low']}
        if not format_price:
            price = self.get_price()
            return {k: round(100 * (price/v),2) for k,v in data.items()}
        return data

    def get_highest_volume_strike(self, weeks, type = 'call'):
        mkt_data = self.get_option_market_data(sorted({option['id']:self.get_option_market_data(option['id'])['volume'] for option in self.get_options(weeks, type)}.items(),key=operator.itemgetter(1),reverse=True)[0][0])
        inst = self.get_url(mkt_data['instrument'])
        return {'Expiration': inst['expiration_date'], 'Strike': inst['strike_price'], 'Mark': mkt_data['mark_price'], 'Volume': mkt_data['volume'], 'Open Interest': mkt_data['open_interest']}

    def get_open_interest(self, weeks, type):
        return sum([int(self.get_option_market_data(option['id'])['open_interest']) for option in self.get_options(weeks,type)])

    def get_option_volume(self, weeks, type):
        return sum([int(self.get_option_market_data(option['id'])['volume']) for option in self.get_options(weeks,type)])

    def get_call_put_spread(self, weeks = 2):
        call = self.get_option_volume(weeks, 'call')
        put = self.get_option_volume(weeks, 'put')
        return call/(call + put)


c = ClientMethods('splk')
print(c.get_highest_volume_strike(1))
