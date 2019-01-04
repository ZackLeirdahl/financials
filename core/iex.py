import time
import requests
import datetime
from functools import wraps
import pandas as pd

class _IEXBase(object):
    _IEX_API_URL = "https://api.iextrading.com/1.0/"
    def __init__(self, *args, **kwargs):
        self.retry_count = kwargs.pop("retry_count", 3)
        self.pause = kwargs.pop("pause", 0.5)
        self.session = _init_session(kwargs.pop("session", None))
        self.json_parse_int = kwargs.pop("json_parse_int", None)
        self.json_parse_float = kwargs.pop("json_parse_float", None)

    @property
    def params(self):
        return {}

    def _validate_response(self, response):
        if response.text == "Unknown symbol":
            raise IEXQueryError()
        json_response = response.json(
            parse_int=self.json_parse_int,
            parse_float=self.json_parse_float)
        if "Error Message" in json_response:
            raise IEXQueryError()
        return json_response

    def _execute_iex_query(self, url):
        pause = self.pause
        for i in range(self.retry_count+1):
            response = self.session.get(url=url, params=self.params)
            if response.status_code == requests.codes.ok:
                return self._validate_response(response)
            time.sleep(pause)
        raise IEXQueryError()

    def _prepare_query(self):
        url = self._IEX_API_URL + self.url
        return url

    def fetch(self):
        url = self._prepare_query()
        return self._execute_iex_query(url)

def output_format(override=None):
    def _output_format(func):
        @wraps(func)
        def _format_wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if self.output_format is 'pandas':
                if override is None:
                    df = pd.DataFrame(response)
                    return df
                else:
                    import warnings
                    warnings.warn("Pandas output not supported for this "
                                  "endpoint. Defaulting to JSON.")
                    if self.key is 'share':
                        return response[self.symbols[0]]
                    else:
                        return response
            else:
                if self.key is 'share':
                    return response[self.symbols[0]]
                return response
        return _format_wrapper
    return _output_format

def price_output_format(override=None):
    def _output_format(func):
        @wraps(func)
        def _format_wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if self.output_format is 'pandas':
                if override is None:
                    if self.key is 'share':
                        return pd.DataFrame({"price": response})
                    else:
                        return pd.DataFrame({"price": response})
                else:
                    import warnings
                    warnings.warn("Pandas output not supported for this "
                                  "endpoint. Defaulting to JSON.")
                    if self.key is 'share':
                        return response[self.symbols[0]]
                    else:
                        return response
            else:
                if self.key is 'share':
                    return response[self.symbols[0]]
                return response
        return _format_wrapper
    return _output_format

def field_output_format(override=None, field_name=None):
    def _output_format(func):
        @wraps(func)
        def _format_wrapper(self, *args, **kwargs):
            data = func(self, *args, **kwargs)

            if self.output_format is 'pandas':
                return data.transpose()
            else:
                if self.key is 'share':
                    return data[field_name]
                else:
                    return {symbol: data[symbol][field_name] for symbol in
                            list(data)}
        return _format_wrapper
    return _output_format

class StockReader(_IEXBase):
    _ENDPOINTS = ["chart", "quote", "book", "open-close", "previous","company", "stats", "peers", "relevant", "news","financials", "earnings", "dividends", "splits", "logo", "price", "delayed-quote", "effective-spread", "volume-by-venue", "ohlc"]

    def __init__(self, symbols=None, output_format='json', **kwargs):
        self.symbols = list(map(lambda x: x.upper(), symbols))
        if len(symbols) == 1: self.key = "share"
        else: self.key = "batch"
        self.output_format = output_format
        self.endpoints = []
        super(StockReader, self).__init__(**kwargs)

    def change_output_format(self, new_format):
        if new_format.lower() not in ['pandas', 'json']: raise ValueError("Please specify a valid output format")
        else: self.output_format = new_format

    @output_format(override='json')
    def get_all(self):
        self.optional_params = {}
        self.endpoints = self._ENDPOINTS[:10]
        json_data = self.fetch()
        self.endpoints = self._ENDPOINTS[10:20]
        json_data_2 = self.fetch()
        for symbol in self.symbols:
            if symbol not in json_data: raise IEXSymbolError(symbol)
            json_data[symbol].update(json_data_2[symbol])
        return json_data

    @property
    def url(self):
        return 'stock/market/batch'

    @property
    def params(self):
        temp = {"symbols": ','.join(self.symbols),"types": ','.join(self.endpoints)}
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
        data = self.fetch()
        for symbol in self.symbols:
            if symbol not in data: raise IEXSymbolError(symbol)
            elif endpoint in data[symbol]:
                if data[symbol][endpoint] is None: raise IEXEndpointError(endpoint)
            else: raise IEXEndpointError(endpoint)
        return data

    @output_format(override='json')
    def get_endpoints(self, endpoints=[]):
        if isinstance(endpoints, str): return self._get_endpoint(endpoints)
        elif not endpoints: raise ValueError("Please provide a valid list of endpoints")
        elif len(endpoints) > 10: raise ValueError("Please input up to 10 valid endpoints")
        self.optional_params = {}
        self.endpoints = endpoints
        json_data = self.fetch()
        for symbol in self.symbols:
            if symbol not in json_data: raise IEXSymbolError(symbol)
        for endpoint in endpoints:
            if endpoint in json_data[self.symbols[0]]:
                if json_data[self.symbols[0]][endpoint] is None: raise IEXEndpointError(endpoint)
            else: raise IEXEndpointError(endpoint)
        return json_data

    @output_format(override=None)
    def get_book(self, **kwargs):
        data = self._get_endpoint("book", kwargs)
        return {symbol: data[symbol]["book"] for symbol in list(data)}

    @output_format(override='json')
    def get_chart(self, **kwargs):
        data = self._get_endpoint("chart", kwargs)
        return {symbol: data[symbol]["chart"] for symbol in list(data)}

    @output_format(override=None)
    def get_company(self, **kwargs):
        data = self._get_endpoint("company", kwargs)
        return {symbol: data[symbol]["company"] for symbol in list(data)}

    @output_format(override=None)
    def get_delayed_quote(self, **kwargs):
        data = self._get_endpoint("delayed-quote", kwargs)
        return {symbol: data[symbol]["delayed-quote"] for symbol in list(data)}

    @output_format(override='json')
    def get_dividends(self, **kwargs):
        data = self._get_endpoint("dividends", kwargs)
        return {symbol: data[symbol]["dividends"] for symbol in list(data)}

    @output_format(override=None)
    def get_earnings(self, **kwargs):
        data = self._get_endpoint("earnings", kwargs)
        return {symbol: data[symbol]["earnings"].get("earnings", []) for symbol in list(data)}

    @output_format(override=None)
    def get_effective_spread(self, **kwargs):
        data = self._get_endpoint("effective-spread", kwargs)
        return {symbol: data[symbol]["effective-spread"] for symbol in list(data)}

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

    @output_format(override=None)
    def get_logo(self, **kwargs):
        data = self._get_endpoint("logo", kwargs)
        return {symbol: data[symbol]["logo"] for symbol in list(data)}

    @output_format(override='json')
    def get_news(self, **kwargs):
        data = self._get_endpoint("news", kwargs)
        return {symbol: data[symbol]["news"] for symbol in list(data)}

    @output_format(override=None)
    def get_ohlc(self, **kwargs):
        data = self._get_endpoint("ohlc", kwargs)
        return {symbol: data[symbol]["ohlc"] for symbol in list(data)}

    def get_open_close(self, **kwargs):
        return self.get_ohlc()

    @output_format(override='json')
    def get_peers(self, **kwargs):
        data = self._get_endpoint("peers", kwargs)
        return {symbol: data[symbol]["peers"] for symbol in list(data)}

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

    @output_format(override=None)
    def get_relevant(self, **kwargs):
        data = self._get_endpoint("relevant", kwargs)
        return {symbol: data[symbol]["relevant"] for symbol in list(data)}

    @output_format(override=None)
    def get_splits(self, **kwargs):
        data = self._get_endpoint("splits", kwargs)
        return {symbol: data[symbol]["splits"] for symbol in list(data)}

    def get_historical_volatility(self, **kwargs):
        import numpy as np
        data = pd.DataFrame(self.get_chart(range='1y'))
        log_return = np.log(data['close'] / data['close'].shift(1))
        return round(np.sqrt(log_return.apply(lambda x: (x-log_return.mean())**2).mean()) * np.sqrt(252),4)

    def get_time_series(self, **kwargs):
        return self.get_chart()

    @output_format(override=None)
    def get_volume_by_venue(self, **kwargs):
        data = self._get_endpoint("volume-by-venue", kwargs)
        return {symbol: data[symbol]["volume-by-venue"] for symbol in list(data)}

    @field_output_format(override=None, field_name="companyName")
    def get_company_name(self):
        return self.get_quote(filter_="companyName")

    @field_output_format(override=None, field_name="primaryExchange")
    def get_primary_exchange(self):
        return self.get_quote(filter_="primaryExchange")

    @field_output_format(override=None, field_name="sector")
    def get_sector(self):
        return self.get_quote(filter_="sector")

    @field_output_format(override=None, field_name="open")
    def get_open(self):
        return self.get_quote(filter_="open")

    @field_output_format(override=None, field_name="close")
    def get_close(self):
        return self.get_quote(filter_="close")

    @field_output_format(override=None, field_name="week52High")
    def get_years_high(self):
        return self.get_quote(filter_="week52High")

    @field_output_format(override=None, field_name="week52Low")
    def get_years_low(self):
        return self.get_quote(filter_="week52Low")

    @field_output_format(override=None, field_name="ytdChange")
    def get_ytd_change(self):
        return self.get_quote(filter_="ytdChange")

    @field_output_format(override=None, field_name="latestVolume")
    def get_volume(self):
        return self.get_quote(filter_="latestVolume")

    @field_output_format(override=None, field_name="marketCap")
    def get_market_cap(self):
        return self.get_quote(filter_="marketCap")

    @field_output_format(override=None, field_name="beta")
    def get_beta(self):
        return self.get_key_stats(filter_="beta")

    @field_output_format(override=None, field_name="shortInterest")
    def get_short_interest(self):
        return self.get_key_stats(filter_="shortInterest")

    @field_output_format(override=None, field_name="shortRatio")
    def get_short_ratio(self):
        return self.get_key_stats(filter_="shortRatio")

    @field_output_format(override=None, field_name="latestEPS")
    def get_latest_eps(self):
        return self.get_key_stats(filter_="latestEPS")

    @field_output_format(override=None, field_name="sharesOutstanding")
    def get_shares_outstanding(self):
        return self.get_key_stats(filter_="sharesOutstanding")

    @field_output_format(override=None, field_name="float")
    def get_float(self):
        return self.get_key_stats(filter_="float")

    @field_output_format(override=None, field_name="consensusEPS")
    def get_eps_consensus(self):
        return self.get_key_stats(filter_="consensusEPS")

    def get_moving_average(self, n):
        return round(list(pd.Series.rolling(pd.DataFrame(self.get_chart(range = '1y'))['close'], n).mean())[-1],2)

    def get_technicals(self):
        return {'MA 20': self.get_moving_average(20), 'MA 50': self.get_moving_average(50), 'MA 100': self.get_moving_average(100), 'MA 200': self.get_moving_average(200), '52 High': self.get_years_high(), '52 Low': self.get_years_low()}

class HistoricalReader(_IEXBase):
    def __init__(self, symbols, start, end, output_format='json', **kwargs):
        if isinstance(symbols, list) and len(symbols) > 1:
            self.type = "Batch"
            self.symlist = symbols
        elif isinstance(symbols, str):
            self.type = "Share"
            self.symlist = [symbols]
        else: raise ValueError("Please input a symbol or list of symbols")
        self.symbols = symbols
        self.start = start
        self.end = end
        self.output_format = output_format
        super(HistoricalReader, self).__init__(**kwargs)

    @property
    def url(self):
        return "stock/market/batch"

    @property
    def key(self):
        return self.type

    @property
    def chart_range(self):
        delta = datetime.datetime.now().year - self.start.year
        if 2 <= delta <= 5: return "5y"
        elif 1 <= delta <= 2: return "2y"
        elif 0 <= delta < 1: return "1y"
        else: raise ValueError("Invalid date specified. Must be within past 5 years.")

    @property
    def params(self):
        if self.type is "Batch": syms = ",".join(self.symbols)
        else: syms = self.symbols
        return { "symbols": syms, "types": "chart", "range": self.chart_range }

    def fetch(self):
        response = super(HistoricalReader, self).fetch()
        for sym in self.symlist:
            if sym not in list(response): raise IEXSymbolError(sym)
        return self._output_format(response)

    def _output_format(self, out):
        result = {}
        for symbol in self.symlist:
            d = out.pop(symbol)["chart"]
            df = pd.DataFrame(d)
            df.set_index("date", inplace=True)
            values = ["open", "high", "low", "close", "volume"]
            df = df[values]
            sstart = self.start.strftime('%Y-%m-%d')
            send = self.end.strftime('%Y-%m-%d')
            df = df.loc[sstart:send]
            result.update({symbol: df})
        if self.output_format is "pandas":
            if len(result) > 1: return result
            return result[self.symbols]
        else:
            for sym in list(result): result[sym] = result[sym].to_dict('index')
            return result

class MoversReader(_IEXBase):
    _AVAILABLE_MOVERS = ["mostactive", "gainers", "losers", "iexvolume", "iexpercent"]

    def __init__(self, mover=None, **kwargs):
        super(MoversReader, self).__init__(**kwargs)
        if mover in self._AVAILABLE_MOVERS: self.mover = mover
        else: raise ValueError("Please input a valid market mover.")

    @property
    def url(self):
        return 'stock/market/list/' + self.mover
class IEXSymbolError(Exception):
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return "Symbol " + self.symbol + " not found."

class IEXEndpointError(Exception):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def __str__(self):
        return "Endpoint " + self.endpoint + " not found."

class IEXFieldError(Exception):
    def __init__(self, endpoint, field):
        self.field = field
        self.endpoint = endpoint

    def __str__(self):
        return ("Field " + self.field + " not found in Endpoint " +
                self.endpoint)

class IEXQueryError(Exception):
    def __str__(self):
        return "An error occurred while making the query."

from datetime import datetime
from pandas import to_datetime

def _init_session(session, retry_count=3):
    if session is None:
        session = requests.session()
    return session

def _sanitize_dates(start, end):
    if isinstance(start, int): start = datetime(start, 1, 1)
    start = to_datetime(start)
    if isinstance(end, int): end = datetime(end, 1, 1)
    end = to_datetime(end)
    if start is None: start = datetime(2015, 1, 1)
    if end is None: end = datetime.today()
    if start > end: raise ValueError('start must be an earlier date than end')
    return start, end
