import six
import logging
import warnings
from enum import Enum
from six.moves.urllib.parse import unquote
from six.moves.urllib.request import getproxies
from six.moves import input
import getpass
import requests
import dateutil
import operator
from datetime import *

class Robinhood:
    session = None
    headers = None
    auth_token = None
    oauth_token = None
    username = 'zackleirdahl@gmail.com'
    password = 'Aksahc123!'
    logger = logging.getLogger('Robinhood')
    logger.addHandler(logging.NullHandler())

    def __init__(self, login = True):
        self.session = requests.session()
        self.session.proxies = getproxies()
        self.headers = {"Accept": "*/*","Accept-Encoding": "gzip, deflate","Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5","Content-Type": "application/x-www-form-urlencoded; charset=utf-8","X-Robinhood-API-Version": "1.0.0","Connection": "keep-alive","User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"}
        self.session.headers = self.headers
        if login: self.login()

    def login(self, username=None, password=None):
        res = self.session.post(login(), data={'password': self.password,'username': self.username,'grant_type': 'password','client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS'}, timeout=15)
        res.raise_for_status()
        data = res.json()
        self.auth_token = data['access_token']
        self.oauth_token = data['access_token']
        self.headers['Authorization'] = 'Bearer ' + self.auth_token
        return True

    def logout(self):
        req = self.session.post(logout(), timeout=15)
        req.raise_for_status()
        self.headers['Authorization'] = None
        self.auth_token = None
        return req

    def investment_profile(self):
        res = self.session.get(investment_profile(), timeout=15)
        res.raise_for_status()
        data = res.json()
        return data

    def instruments(self, stock):
        res = self.session.get(instruments(), params={'query': stock.upper()}, timeout=15)
        res.raise_for_status()
        res = res.json()
        if (stock == ""): return res
        return res['results']

    def instrument(self, id):
        url = str(instruments()) + str(id) + "/"
        req = requests.get(url, timeout=15)
        req.raise_for_status()
        data = req.json()
        return data

    def quote_data(self, stock=''):
        url = str(quotes()) + "?symbols=" + str(stock)
        req = requests.get(url, timeout=15)
        req.raise_for_status()
        data = req.json()
        return data

    def quotes_data(self, stocks):
        url = str(quotes()) + "?symbols=" + ",".join(stocks)
        req = requests.get(url, timeout=15)
        req.raise_for_status()
        data = req.json()
        return data["results"]

    def get_quote_list(self, stock='', key=''):
        def append_stock(stock):
            keys = key.split(',')
            myStr = ''
            for item in keys:
                myStr += stock[item] + ","
            return (myStr.split(','))
        if not stock:
            stock = input("Symbol: ")
        data = self.quote_data(stock)
        res = []
        if stock.find(',') != -1:
            for stock in data['results']:
                if stock is None:
                    continue
                res.append(append_stock(stock))
        else:
            res.append(append_stock(data))
        return res

    def get_quote(self, stock=''):
        return self.quote_data(stock)["symbol"]

    def get_historical_quotes(self, stock, interval, span):
        if type(stock) is str: stock = [stock]
        params = {'symbols': ','.join(stock).upper(),'interval': interval,'span': span, 'bounds': 'regular'}
        res = self.session.get(historicals(), params=params, timeout=15)
        return res.json()

    def get_news(self, stock):
        return self.session.get(news(stock.upper()), timeout=15).json()

    def ask_price(self, stock=''):
        return self.get_quote_list(stock, 'ask_price')

    def ask_size(self, stock=''):
        return self.get_quote_list(stock, 'ask_size')

    def bid_price(self, stock=''):
        return self.get_quote_list(stock, 'bid_price')

    def bid_size(self, stock=''):
        return self.get_quote_list(stock, 'bid_size')

    def last_trade_price(self, stock=''):
        return self.get_quote_list(stock, 'last_trade_price')

    def previous_close(self, stock=''):
        return self.get_quote_list(stock, 'previous_close')

    def previous_close_date(self, stock=''):
        return self.get_quote_list(stock, 'previous_close_date')

    def adjusted_previous_close(self, stock=''):
        return self.get_quote_list(stock, 'adjusted_previous_close')

    def symbol(self, stock=''):
        return self.get_quote_list(stock, 'symbol')

    def last_updated_at(self, stock=''):
        return self.get_quote_list(stock, 'last_updated_at')

    def last_updated_at_datetime(self, stock=''):
        datetime_string = self.last_updated_at(stock)
        result = dateutil.parser.parse(datetime_string)
        return result

    def get_account(self):
        res = self.session.get(accounts(), timeout=15)
        res.raise_for_status()
        res = res.json()
        return res['results'][0]

    def get_url(self, url):
        return self.session.get(url, timeout=15).json()

    def get_popularity(self, stock=''):
        stock_instrument = self.get_url(self.quote_data(stock)["instrument"])["id"]
        return self.get_url(instruments(stock_instrument, "popularity"))["num_open_positions"]

    def get_tickers_by_tag(self, tag=None):
        instrument_list = self.get_url(tags(tag))["instruments"]
        return [self.get_url(instrument)["symbol"] for instrument in instrument_list]

    def get_options(self, stock, num_weeks, option_type):
        expiration_dates = get_dates(num_weeks)
        instrumentid = self.instruments(stock)[0]['id']
        if(type(expiration_dates) == list):
            _expiration_dates_string = ','.join(expiration_dates)
        else:
            _expiration_dates_string = expiration_dates
        chain_id = self.get_url(chain(instrumentid))["results"][0]["id"]
        return [contract for contract in self.get_url(options(chain_id, _expiration_dates_string, option_type))["results"]]

    def get_option_market_data(self, optionid):
        return self.get_url(market_data(optionid))

    def get_fundamentals(self, stock=''):
        url = str(fundamentals(str(stock.upper())))
        req = requests.get(url, timeout=15)
        req.raise_for_status()
        return req.json()

    def fundamentals(self, stock=''):
        return self.get_fundamentals(stock)

    def portfolios(self):
        req = self.session.get(portfolios(), timeout=15)
        req.raise_for_status()
        return req.json()['results'][0]

    def adjusted_equity_previous_close(self):
        return float(self.portfolios()['adjusted_equity_previous_close'])

    def equity(self):
        return float(self.portfolios()['equity'])

    def equity_previous_close(self):
        return float(self.portfolios()['equity_previous_close'])

    def excess_margin(self):
        return float(self.portfolios()['excess_margin'])

    def extended_hours_equity(self):
        return float(self.portfolios()['extended_hours_equity'])

    def extended_hours_market_value(self):
        return float(self.portfolios()['extended_hours_market_value'])

    def last_core_equity(self):
        return float(self.portfolios()['last_core_equity'])

    def last_core_market_value(self):
        return float(self.portfolios()['last_core_market_value'])

    def market_value(self):
        return float(self.portfolios()['market_value'])

    def order_history(self, orderId=None):
        return self.session.get(orders(orderId), timeout=15).json()

    def dividends(self):
        return self.session.get(dividends(), timeout=15).json()

    def positions(self):
        return self.session.get(positions(), timeout=15).json()

    def securities_owned(self):
        return self.session.get(positions() + '?nonzero=true', timeout=15).json()['results']

    def get_options_positions(self, results = []):
        for res in self.session.get(option_positions(),timeout=15).json()['results']:
            if float(res['quantity']) > 0: results.append(res)
        return results

    def get_highest_volume_strike(self, stock, num_weeks, type = 'call'):
        records = {option['id']:self.get_option_market_data(option['id'])['volume'] for option in self.get_options(stock, get_dates(num_weeks), type)}
        data = sorted(records.items(), key=operator.itemgetter(1),reverse=True)[0]
        mkt_data = self.get_option_market_data(data[0])
        inst = self.get_url(mkt_data['instrument'])
        return {'Expiration': inst['expiration_date'], 'Strike': inst['strike_price'], 'Mark': mkt_data['mark_price'], 'Volume': mkt_data['volume'], 'Open Interest': mkt_data['open_interest']}

def get_dates(arg):
    if type(arg) == int:
        return [str(date.fromordinal(date.today().toordinal() + ((1+i)*{0:4,1:3,2:2,3:1,4:7,5:6,6:5}[date.today().weekday()]))) for i in range(arg)]

def option_positions():
    return "https://api.robinhood.com/options/positions/"

def login():
    return "https://api.robinhood.com/oauth2/token/"

def logout():
    return "https://api.robinhood.com/api-token-logout/"

def investment_profile():
    return "https://api.robinhood.com/user/investment_profile/"

def accounts():
    return "https://api.robinhood.com/accounts/"

def ach(option):
    return "https://api.robinhood.com/ach/iav/auth/" if option == "iav" else "https://api.robinhood.com/ach/{_option}/".format(_option=option)

def applications():
    return "https://api.robinhood.com/applications/"

def dividends():
    return "https://api.robinhood.com/dividends/"

def edocuments():
    return "https://api.robinhood.com/documents/"

def instruments(instrumentId=None, option=None):
    return "https://api.robinhood.com/instruments/" + ("{id}/".format(id=instrumentId) if instrumentId else "") + ("{_option}/".format(_option=option) if option else "")

def margin_upgrades():
    return "https://api.robinhood.com/margin/upgrades/"

def markets():
    return "https://api.robinhood.com/markets/"

def notifications():
    return "https://api.robinhood.com/notifications/"

def orders(orderId=None):
    return "https://api.robinhood.com/orders/" + ("{id}/".format(id=orderId) if orderId else "")

def password_reset():
    return "https://api.robinhood.com/password_reset/request/"

def portfolios():
    return "https://api.robinhood.com/portfolios/"

def positions():
    return "https://api.robinhood.com/positions/"

def option_position():
    return "https://api.robinhood.com/options/instruments/"

def quotes():
    return "https://api.robinhood.com/quotes/"

def historicals():
    return "https://api.robinhood.com/quotes/historicals/"

def document_requests():
    return "https://api.robinhood.com/upload/document_requests/"

def user():
    return "https://api.robinhood.com/user/"

def watchlists():
    return "https://api.robinhood.com/watchlists/"

def news(stock):
    return "https://api.robinhood.com/midlands/news/{_stock}/".format(_stock=stock)

def fundamentals(stock):
    return "https://api.robinhood.com/fundamentals/{_stock}/".format(_stock=stock)

def tags(tag=None):
    return "https://api.robinhood.com/midlands/tags/tag/{_tag}/".format(_tag=tag)

def chain(instrumentid):
    return "https://api.robinhood.com/options/chains/?equity_instrument_ids={_instrumentid}".format(_instrumentid=instrumentid)

def options(chainid, dates, option_type):
    return "https://api.robinhood.com/options/instruments/?chain_id={_chainid}&expiration_dates={_dates}&state=active&tradability=tradable&type={_type}".format(_chainid=chainid, _dates=dates, _type=option_type)

def market_data(optionid):
    return "https://api.robinhood.com/marketdata/options/{_optionid}/".format(_optionid=optionid)

def convert_token():
    return "https://api.robinhood.com/oauth2/migrate_token/"
