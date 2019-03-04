from datetime import *
import pandas as pd
from functools import wraps
import dateutil
import numpy as np
from math import *

_endpoints = ["chart", "quote", "book", "open-close", "previous","company", "stats", "peers", "relevant", "news","financials", "earnings", "dividends", "splits", "logo", "price", "delayed-quote", "effective-spread", "volume-by-venue", "ohlc"]

def output_format(override=None):
    def _output_format(func):
        @wraps(func)
        def _format_wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if self.output_format is 'pandas':
                if override is None: return pd.DataFrame(response)
                else: return response[self.symbol]
            else: return response[self.symbol]
        return _format_wrapper
    return _output_format

def price_output_format(override=None):
    def _output_format(func):
        @wraps(func)
        def _format_wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if self.output_format is 'pandas':
                if override is None: return pd.DataFrame({"price": response})
                else: return response[self.symbol]
            else: return response[self.symbol]
        return _format_wrapper
    return _output_format

def field_output_format(override=None, field_name=None):
    def _output_format(func):
        @wraps(func)
        def _format_wrapper(self, *args, **kwargs):
            data = func(self, *args, **kwargs)
            if self.output_format is 'pandas': return data.transpose()
            else: return data[field_name]
        return _format_wrapper
    return _output_format

def get_dates(weeks):
    return ','.join([str(date.fromordinal(date.today().toordinal() + ((1+i)*{0:4,1:3,2:2,3:1,4:7,5:6,6:5}[date.today().weekday()]))) for i in range(weeks)])

def instruments(instrumentId=None, option=None):
    return "https://api.robinhood.com/instruments/" + ("{id}/".format(id=instrumentId) if instrumentId else "") + ("{_option}/".format(_option=option) if option else "")

def news(stock):
    return "https://api.robinhood.com/midlands/news/{_stock}/".format(_stock=stock)

def tags(tag=None):
    return "https://api.robinhood.com/midlands/tags/tag/{_tag}/".format(_tag=tag)

def chain(instrumentid):
    return "https://api.robinhood.com/options/chains/?equity_instrument_ids={_instrumentid}".format(_instrumentid=instrumentid)

def options(chainid, dates, option_type):
    return "https://api.robinhood.com/options/instruments/?chain_id={_chainid}&expiration_dates={_dates}&state=active&tradability=tradable&type={_type}".format(_chainid=chainid, _dates=dates, _type=option_type)

def market_data(optionid):
    return "https://api.robinhood.com/marketdata/options/{_optionid}/".format(_optionid=optionid)

def historicals():
    return "https://api.robinhood.com/quotes/historicals/"

def positions():
    return "https://api.robinhood.com/positions/"

def option_positions():
    return "https://api.robinhood.com/options/positions/"

def token():
    return "https://api.robinhood.com/oauth2/token/"

def get_theoretical_mark(stock, strike, imp_vol, expiration_date, price, option_type = 'call', interest_rate= 0.025):
    maturity_time = (date.fromordinal(datetime.strptime(expiration_date,'%Y-%m-%d').toordinal()) - date.today()).days / 365
    d1 = (np.log(price / strike) + (interest_rate + 0.5 * imp_vol ** 2) * maturity_time) / (imp_vol * np.sqrt(maturity_time))
    d2 = (np.log(price / strike) + (interest_rate - 0.5 * imp_vol ** 2) * maturity_time) / (imp_vol * np.sqrt(maturity_time))
    options = {'call':(price * cumulative_normal_dist(d1) - strike * np.exp(-interest_rate * maturity_time) * cumulative_normal_dist(d2)), 'put': (strike * np.exp(-interest_rate * maturity_time) * cumulative_normal_dist(-d2) - price * cumulative_normal_dist(-d1))}
    return options[option_type]

def cumulative_normal_dist(derivative):
    dist = 1-1/sqrt(2*pi)*exp(-abs(derivative)*abs(derivative)/2.)*(0.31938153*(1.0/(1.0+0.2316419* abs(derivative)))+-0.356563782*(1.0/(1.0+0.2316419* abs(derivative)))*(1.0/(1.0+0.2316419* abs(derivative)))+1.781477937*pow((1.0/(1.0+0.2316419* abs(derivative))),3)+-1.821255978*pow((1.0/(1.0+0.2316419* abs(derivative))),4)+1.330274429*pow((1.0/(1.0+0.2316419* abs(derivative))),5))
    if derivative < 0: return 1-dist
    return dist
