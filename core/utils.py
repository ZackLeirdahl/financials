from datetime import *
import pandas as pd
from functools import wraps
import dateutil, requests, inspect
import numpy as np
from math import *
from const import api_base, authorizations
from pyEX import Client

def login_required(function):
    def wrapper(self, *args, **kwargs):
        if 'Authorization' not in self.headers:
            self.login()
        return function(self, *args, **kwargs)
    return wrapper

def _retry(func):
    @wraps(func)
    def _retry_wrapper(self, *args, **kwargs):
        for i in range(5):
            try: return func(self, *args, **kwargs)
            except: continue
        raise ValueError('Retry account exceeded.')
    return _retry_wrapper

def api_call(func):
    argspec = inspect.getargspec(func)
    try:
        positional_count = len(argspec.args) - len(argspec.defaults)
        defaults = dict(zip(argspec.args[positional_count:], argspec.defaults))
    except TypeError:
        if argspec.args:
            positional_count = len(argspec.args)
            defaults = {}
        elif argspec.defaults:
            positional_count = 0
            defaults = argspec.defaults
    @wraps(func)
    def _call_wrapper(self, *args, **kwargs):
        used_kwargs = kwargs.copy()
        used_kwargs.update(zip(argspec.args[positional_count:],args[positional_count:]))
        used_kwargs.update({k: used_kwargs.get(k, d) for k, d in defaults.items()})
        function_name, data_key, meta_data_key = func(self, *args, **kwargs)
        url = '{}&{}={}'.format('{}function={}'.format(api_base['alphavantage'],function_name), 'symbol', self.symbol)
        for idx, arg_name in enumerate(argspec.args[1:]):
            try: arg_value = args[idx]
            except: arg_value = used_kwargs[arg_name]
            if 'matype' in arg_name and arg_value:
                arg_value = ['SMA','EMA','WMA','DEMA','TEMA','TRIMA','T3','KAMA','MAMA'].index(arg_value)
            if arg_value:
                if isinstance(arg_value, tuple) or isinstance(arg_value, list): arg_value = ','.join(arg_value)
                url = '{}&{}={}'.format(url, arg_name, arg_value)
        return _handle_api_call('{}&apikey={}&datatype={}'.format(url, authorizations['alphavantage'], 'json')), data_key, meta_data_key
    return _call_wrapper

def output_format(func, override=None):
    @wraps(func)
    def _format_wrapper(self, *args, **kwargs):
        call_response, data_key, meta_data_key = func(self, *args, **kwargs)
        data = call_response[data_key]
        if self.output_format.lower() == 'json':
            return data, call_response[meta_data_key]
        else:
            return pd.DataFrame.from_dict(data, orient='index', dtype=float), call_response[meta_data_key]
    return _format_wrapper

@_retry
def _handle_api_call(url):
    return requests.get(url, proxies={}).json()

def instruments(instrumentId=None, option=None):
    return 'https://api.robinhood.com/instruments/' + ('{id}/'.format(id=instrumentId) if instrumentId else '') + ('{_option}/'.format(_option=option) if option else '')

def news(stock):
    return 'https://api.robinhood.com/midlands/news/{_stock}/'.format(_stock=stock)

def tags(tag=None):
    return 'https://api.robinhood.com/midlands/tags/tag/{_tag}/'.format(_tag=tag)

def chain(instrumentid):
    return 'https://api.robinhood.com/options/chains/?equity_instrument_ids={_instrumentid}'.format(_instrumentid=instrumentid)

def options(chainid, dates, option_type):
    return 'https://api.robinhood.com/options/instruments/?chain_id={_chainid}&expiration_dates={_dates}&state=active&tradability=tradable&type={_type}'.format(_chainid=chainid, _dates=dates, _type=option_type)

def market_data(optionid):
    return 'https://api.robinhood.com/marketdata/options/{_optionid}/'.format(_optionid=optionid)

def historicals():
    return 'https://api.robinhood.com/quotes/historicals/'

def positions():
    return 'https://api.robinhood.com/positions/'

def option_positions():
    return 'https://api.robinhood.com/options/positions/'

def token():
    return 'https://api.robinhood.com/oauth2/token/'

def get_dates(weeks):
    return ','.join([str(date.fromordinal(ord)) for ord in check_holiday([get_next_friday(i) for i in range(weeks)])])

def get_next_friday(i):
    return (7*i) + date.today().toordinal() + {0:4,1:3,2:2,3:1,4:7,5:6,6:5}[date.today().weekday()]

def check_holiday(ords):
    new_ords = []
    c = Client(authorizations['pyEX'])
    holiday_ords = [holiday.toordinal() for holiday in c.calendarDF(type='holiday',direction='next',last = 10)['date'].tolist()]
    for ord in ords:
        if ord in holiday_ords:
            ord -=1
        new_ords.append(ord)
    return new_ords

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
