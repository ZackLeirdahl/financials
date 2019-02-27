from datetime import *
import pandas as pd
from functools import wraps
import dateutil
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
