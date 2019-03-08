import requests
from six.moves.urllib.request import getproxies
from utils import *

class StockReader(object):
    def __init__(self, symbol=None, login = True, output_format='json', retry_count = 5, **kwargs):
        self.symbol = symbol.upper()
        self.output_format = output_format
        self.retry_count = retry_count
        self.endpoints = []
        self.iex_session = requests.session()
        self.robinhood_session = requests.session()
        self.robinhood_session.proxies = getproxies()
        self.headers = {"Accept": "*/*","Accept-Encoding": "gzip, deflate","Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5","Content-Type": "application/x-www-form-urlencoded; charset=utf-8","X-Robinhood-API-Version": "1.0.0","Connection": "keep-alive","User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"}
        self.robinhood_session.headers = self.headers
        if login: self.login()

    def login(self):
        res = self.robinhood_session.post(token(), data={'password': 'Aksahc123!','username': 'zackleirdahl@gmail.com','grant_type': 'password','client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS'}, timeout=15)
        res.raise_for_status()
        self.headers['Authorization'] = 'Bearer ' + res.json()['access_token']

    def _execute_iex_query(self):
        for i in range(self.retry_count + 1):
            response = self.iex_session.get(url="https://api.iextrading.com/1.0/stock/market/batch", params=self.params)
            if response.status_code == requests.codes.ok:
                return response.json(parse_int=None, parse_float=None)
        raise ValueError("An error occurred while making the query.")

    @property
    def params(self):
        temp = {"symbols": self.symbol, "types": ','.join(self.endpoints)}
        temp.update({key: self.optional_params[key] for key in self.optional_params})
        if "filter_" in temp:
            if isinstance(temp["filter_"], list): temp["filter"] = ",".join(temp.pop("filter_"))
            else: temp["filter"] = temp.pop("filter_")
        if "range_" in temp: temp["range"] = temp.pop("range_")
        params = {k: str(v).lower() if v is True or v is False else str(v) for k, v in temp.items()}
        return params

    def _get_endpoint(self, endpoint, params={}):
        self.optional_params = params
        self.endpoints = [endpoint]
        return self._execute_iex_query()

    @output_format(override='json')
    def get_chart(self, **kwargs):
        data = self._get_endpoint("chart", kwargs)
        return {symbol: data[symbol]["chart"] for symbol in list(data)}

    @output_format(override=None)
    def get_company(self, **kwargs):
        data = self._get_endpoint("company", kwargs)
        return {symbol: data[symbol]["company"] for symbol in list(data)}

    @output_format(override=None)
    def get_earnings(self, **kwargs):
        data = self._get_endpoint("earnings", kwargs)
        return {symbol: data[symbol]["earnings"].get("earnings", []) for symbol in list(data)}

    @output_format(override=None)
    def get_financials(self, **kwargs):
        data = self._get_endpoint("financials", kwargs)
        return {symbol: data[symbol]["financials"].get("financials", []) for symbol in list(data)}

    @output_format(override=None)
    def get_key_stats(self, **kwargs):
        data = self._get_endpoint("stats", kwargs)
        return {symbol: data[symbol]["stats"] for symbol in list(data)}

    @output_format(override=None)
    def get_largest_trades(self, **kwargs):
        data = self._get_endpoint("largest-trades", kwargs)
        return {symbol: data[symbol]["largest-trades"] for symbol in list(data)}

    @output_format(override='json')
    def get_news(self, **kwargs):
        #['related', 'source', 'summary', 'image', 'datetime', 'headline', 'url']
        data = self._get_endpoint("news", kwargs)
        return {symbol: data[symbol]["news"] for symbol in list(data)}

    @output_format(override=None)
    def get_ohlc(self, **kwargs):
        data = self._get_endpoint("ohlc", kwargs)
        return {symbol: data[symbol]["ohlc"] for symbol in list(data)}

    @output_format(override=None)
    def get_previous(self, **kwargs):
        data = self._get_endpoint("previous", kwargs)
        return {symbol: data[symbol]["previous"] for symbol in list(data)}

    @price_output_format(override=None)
    def get_price(self, **kwargs):
        data = self._get_endpoint("price", kwargs)
        return {symbol: data[symbol]["price"] for symbol in list(data)}

    @output_format(override=None)
    def get_quote(self, **kwargs):
        data = self._get_endpoint("quote", kwargs)
        return {symbol: data[symbol]["quote"] for symbol in list(data)}

    @field_output_format(override=None, field_name="latestVolume")
    def get_volume(self):
        return self.get_quote(filter_="latestVolume")

    def instruments(self):
        res = self.robinhood_session.get(instruments(), params={'query': self.symbol}, timeout=15)
        res.raise_for_status()
        return res.json()['results']

    def instrument(self, id):
        req = requests.get(str(instruments()) + str(id) + "/", timeout=15)
        req.raise_for_status()
        return req.json()

    def get_historical_quotes(self, interval, span):
        res = self.robinhood_session.get(historicals(), params={'symbols': self.symbol,'interval': interval,'span': span, 'bounds': 'regular'}, timeout=15)
        return res.json()

    def get_url(self, url):
        return self.robinhood_session.get(url, timeout=15).json()

    def get_tickers_by_tag(self, tag=None):
        return [self.get_url(instrument)["symbol"] for instrument in self.get_url(tags(tag))["instruments"]]

    def get_options(self, weeks, option_type):
        return [contract for contract in self.get_url(options(self.get_url(chain(self.instruments()[0]['id']))["results"][0]["id"], get_dates(weeks), option_type))["results"]]

    def get_option_market_data(self, optionid):
        return self.get_url(market_data(optionid))

    def get_options_positions(self):
        return list(filter(lambda k: float(k['quantity']) > 0, self.robinhood_session.get(option_positions(),timeout=15).json()['results']))
