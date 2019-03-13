from datetime import *
import pandas as pd
from functools import wraps
import dateutil, requests, inspect
import numpy as np
from math import *

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
        url = '{}&{}={}'.format('{}function={}'.format('http://www.alphavantage.co/query?',function_name), 'symbol', self.symbol)
        for idx, arg_name in enumerate(argspec.args[1:]):
            try: arg_value = args[idx]
            except: arg_value = used_kwargs[arg_name]
            if 'matype' in arg_name and arg_value:
                arg_value = ['SMA','EMA','WMA','DEMA','TEMA','TRIMA','T3','KAMA','MAMA'].index(arg_value)
            if arg_value:
                if isinstance(arg_value, tuple) or isinstance(arg_value, list): arg_value = ','.join(arg_value)
                url = '{}&{}={}'.format(url, arg_name, arg_value)
        return _handle_api_call('{}&apikey={}&datatype={}'.format(url, self.alpha_key, 'json')), data_key, meta_data_key
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

def get_dates(weeks):
    return ','.join([str(date.fromordinal(date.today().toordinal() + ((1+i)*{0:4,1:3,2:2,3:1,4:7,5:6,6:5}[date.today().weekday()]))) for i in range(weeks)])

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

def authorization(client):
    return {'robinhood': {'password': 'Aksahc123!','username': 'zackleirdahl@gmail.com','grant_type': 'password','client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS'},
    'alphavantage':'RBB6OP1B4WXFUIK7',
    'firebase':{
        'type': 'service_account',
        'project_id': 'trader-3870e',
        'private_key_id': '863abdb2e1aef2fb68da60cb755403b2f41251dd',
        'client_email': 'firebase-adminsdk-ht79b@trader-3870e.iam.gserviceaccount.com',
        'client_id': '102596070638584732824',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ht79b%40trader-3870e.iam.gserviceaccount.com',
        'private_key': "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDEMCNGWULUaP2o\nWfFtLS/0Ui6Duhnc03gJm1UlkVI1GRRjoLYpxOMddl4pTfgp2JmklMuzg/AfvYeG\n9lrJAcvxgFTL4BfBtt4AvenS7D8nrl4G8qPwJPfYea8iP6cP3aZ2ys5bCKbL+HZd\nfxCjBzUSy4vFD4bdf4KDkWb3dNUYW979Gkd6+vokSrfYn03w1H0JZPRzVk7aitxa\npvvjVvSmz4jr0JMHnLDzsW2tuYPBMPDkcXd+d6bHdAzBBmxConhICgNyyrCYXURi\n9PDdo8SxQSFYJaGu5wyUFPC7bTT4F8+S0PJkBWGUNbtpciXPAzm/     KGwSzv96TeFh\nRH4lFUSvAgMBAAECggEAE2NAcSjMCmqvuo3c5nGjPg1LDHh9Ks35HFXt5a8FRTsL\nwUa2Cc2rthMm/gT3A8ekc1fDA6QDvFdCB+vbj+auDVklyBoGrv2P1dnuvAndueGo\n6B3dZpN4rLtlu8g3jcFVPIMRPnzN4vVUWSv/7GR/cbKMxvYgWU5LCw548vZoQqZQ\n9j8FHv2//65SH4BWmT6O51uWEZDwMYzeCdhoZBRcgR7kkvOW4Z9jQaU9PQSc/Em9\nD6dNCxOIXvkP/LgtOq8LM7mmw+yJrnEOJWunBntLGInaBnu6TUocvGO7i+EQKVKR\nQtUHByRs2FNv8AO0Fzlf357cU2zH6ZYwbcMZkXzizQKBgQD86LkSKpGjXWK+uekz\nSGl7i4MTk/V2fO/CJ+RqQ6L+P9UEPOH26SCJsdDopqlLDdNvLP+i64bg6jbMMSPR\nK2Y9wqNxNhT1dyQBNnoZcM5pKa+oPHjhYiu+beh2M6DtV9JJinWcRpv/FHbbEG+t\nlZkl+WBGC2D1GXfvBRT+VufauwKBgQDGlfOfmml/Ws41fEtWGqBm0ugMME+FmHCv\nkHte1NuGt8vyeigHuXEmU75fWQKBWyumEP/sjWJHPNHHR8zeIoySoxd1EBdR/MUb\neCS7ocmnghN08ckPtbhcBfC3LlfFU/6CUi7LXdfnerv17n9GDAS0fd88GAb1jXBC\n9WmwwbpgnQJ/Qy2N+0VTahFkKUU4rGaPnkFwj8K9cLu+89Ok2JUetmo+KuIBI5TJ\nD8ors6CRV15UyzMotB3bteKAq7xhxy2/+qe4wlmbN5ht9+SAikFskoKAJi/p6/Qn\nqm2HUd5k4KZzNRWSJ/CZfyfwaj/zaihShcO3zuM23ePl95dh/C0ZaQKBgCQ3VKbW\n0kaXmOPINzUMxhP6grc2WEpU8rgR8W3qA98dxeQCwyold601uJJK+Vn99ofiscnC\nPxoezWM6hPI9+sUDWVPQC3C4WHoZ/xj4+H3ECyhYsAJdcbHWo3/Ew90I5HF/62jL\nRITCrWS8ihmMN49zJTMgbqR5lu+fMhc6PXNBAoGBAOhXy9kNm5FvsSTiJXsl2kxm\nH8cUyphFNxvtE2yeIrkYNUAzp1ridBjh13GANxPNTYLLYZlQOE5K1lZQOGcRB0gm\nrJbD/OtPh+i+FZXGSVDT7AXw4/H2UDQGDhgmhMh0oRSahLldH9QVw/K2xHNmkexb\npwH5cuASXaxnyFFecZLo\n-----END PRIVATE KEY-----\n"},
    'firebase_project': {'projectId':'trader-3870e'}}[client]

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
