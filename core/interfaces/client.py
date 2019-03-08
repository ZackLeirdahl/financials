import requests
from six.moves.urllib.request import getproxies
from utils import *
from authorization import _tokens

class Client(object):
    def __init__(self, symbol=None, login = True, output_format='json', retry_count = 5, **kwargs):
        self.symbol = symbol.upper()
        self.output_format = output_format
        self.retry_count = retry_count
        self.endpoints = []
        self.alpha_key = _tokens['alphavantage']
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

    @output_format_av
    @call_api_on_func
    def get_intraday(self, interval='15min', outputsize='compact'):
        return "TIME_SERIES_INTRADAY", "Time Series ({})".format(interval), 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_intraday(self, interval='15min', outputsize='compact'):
        return "TIME_SERIES_INTRADAY", "Time Series ({})".format(interval), 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_daily(self, outputsize='compact'):
        return "TIME_SERIES_DAILY", 'Time Series (Daily)', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_daily_adjusted(self, outputsize='compact'):
        return "TIME_SERIES_DAILY_ADJUSTED", 'Time Series (Daily)', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_weekly(self):
        return "TIME_SERIES_WEEKLY", 'Weekly Time Series', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_weekly_adjusted(self):
        return "TIME_SERIES_WEEKLY_ADJUSTED", 'Weekly Adjusted Time Series', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_monthly(self):
        return "TIME_SERIES_MONTHLY", 'Monthly Time Series', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_monthly_adjusted(self):
        return "TIME_SERIES_MONTHLY_ADJUSTED", 'Monthly Adjusted Time Series', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_sma(self, interval='daily', time_period=20, series_type='close'):
        return "SMA", 'Technical Analysis: SMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ema(self, interval='daily', time_period=20, series_type='close'):
        return "EMA", 'Technical Analysis: EMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_wma(self, interval='daily', time_period=20, series_type='close'):
        return "WMA", 'Technical Analysis: WMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_dema(self, interval='daily', time_period=20, series_type='close'):
        return "DEMA", 'Technical Analysis: DEMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_tema(self, interval='daily', time_period=20, series_type='close'):
        return "TEMA", 'Technical Analysis: TEMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_trima(self, interval='daily', time_period=20, series_type='close'):
        return "TRIMA", 'Technical Analysis: TRIMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_kama(self, interval='daily', time_period=20, series_type='close'):
        return "KAMA", 'Technical Analysis: KAMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_mama(self, interval='daily', series_type='close', fastlimit=None, slowlimit=None):
        return "MAMA", 'Technical Analysis: MAMA', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_t3(self, interval='daily', time_period=20, series_type='close'):
        return "T3", 'Technical Analysis: T3', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_macd(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, signalperiod=None):
        return "MACD", 'Technical Analysis: MACD', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_macdext(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, signalperiod=None, fastmatype=None, slowmatype=None, signalmatype=None):
        return "MACDEXT", 'Technical Analysis: MACDEXT', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_stoch(self, interval='daily', fastkperiod=None, slowkperiod=None, slowdperiod=None, slowkmatype=None, slowdmatype=None):
        return "STOCH", 'Technical Analysis: STOCH', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_stochf(self, interval='daily', fastkperiod=None, fastdperiod=None, fastdmatype=None):
        _FUNCTION_KEY = "STOCHF"
        return "STOCHF", 'Technical Analysis: STOCHF', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_rsi(self, interval='daily', time_period=20, series_type='close'):
        return "RSI", 'Technical Analysis: RSI', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_stochrsi(self, interval='daily', time_period=20, series_type='close', fastkperiod=None, fastdperiod=None, fastdmatype=None):
        return "STOCHRSI", 'Technical Analysis: STOCHRSI', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_willr(self, interval='daily', time_period=20):
        return "WILLR", 'Technical Analysis: WILLR', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_adx(self, interval='daily', time_period=20):
        return "ADX", 'Technical Analysis: ADX', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_adxr(self, interval='daily', time_period=20):
        return "ADXR", 'Technical Analysis: ADXR', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_apo(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, matype=None):
        return "APO", 'Technical Analysis: APO', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ppo(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, matype=None):
        return "PPO", 'Technical Analysis: PPO', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_mom(self, interval='daily', time_period=20, series_type='close'):
        return "MOM", 'Technical Analysis: MOM', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_bop(self, interval='daily', time_period=20):
        return "BOP", 'Technical Analysis: BOP', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_cci(self, interval='daily', time_period=20):
        return "CCI", 'Technical Analysis: CCI', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_cmo(self, interval='daily', time_period=20, series_type='close'):
        return "CMO", 'Technical Analysis: CMO', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_roc(self, interval='daily', time_period=20, series_type='close'):
        return "ROC", 'Technical Analysis: ROC', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_rocr(self, interval='daily', time_period=20, series_type='close'):
        return "ROCR", 'Technical Analysis: ROCR', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_aroon(self, interval='daily', time_period=20, series_type='close'):
        return "AROON", 'Technical Analysis: AROON', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_aroonosc(self, interval='daily', time_period=20, series_type='close'):
        return "AROONOSC", 'Technical Analysis: AROONOSC', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_mfi(self, interval='daily', time_period=20, series_type='close'):
        return "MFI", 'Technical Analysis: MFI', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_trix(self, interval='daily', time_period=20, series_type='close'):
        return "TRIX", 'Technical Analysis: TRIX', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ultsoc(self, interval='daily', timeperiod1=None, timeperiod2=None, timeperiod3=None):
        return "ULTOSC", 'Technical Analysis: ULTOSC', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_dx(self, interval='daily', time_period=20, series_type='close'):
        return "DX", 'Technical Analysis: DX', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_minus_di(self, interval='daily', time_period=20):
        return "MINUS_DI", 'Technical Analysis: MINUS_DI', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_plus_di(self, interval='daily', time_period=20):
        return "PLUS_DI", 'Technical Analysis: PLUS_DI', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_minus_dm(self, interval='daily', time_period=20):
        return "MINUS_DM", 'Technical Analysis: MINUS_DM', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_plus_dm(self, interval='daily', time_period=20):
        return "PLUS_DM", 'Technical Analysis: PLUS_DM', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_bbands(self, interval='daily', time_period=20,  series_type='close', nbdevup=None, nbdevdn=None, matype=None):
        return "BBANDS", 'Technical Analysis: BBANDS', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_midpoint(self, interval='daily', time_period=20, series_type='close'):
        return "MIDPOINT", 'Technical Analysis: MIDPOINT', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_midprice(self, interval='daily', time_period=20):
        return "MIDPRICE", 'Technical Analysis: MIDPRICE', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_sar(self, interval='daily', acceleration=None, maximum=None):
        return "SAR", 'Technical Analysis: SAR', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_trange(self, interval='daily'):
        return "TRANGE", 'Technical Analysis: TRANGE', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_atr(self, interval='daily', time_period=20):
        return "ATR", 'Technical Analysis: ATR', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_natr(self, interval='daily', time_period=20):
        return "NATR", 'Technical Analysis: NATR', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ad(self, interval='daily'):
        return "AD", 'Technical Analysis: Chaikin A/D', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_adosc(self, interval='daily', fastperiod=None, slowperiod=None):
        return "ADOSC", 'Technical Analysis: ADOSC', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_obv(self, interval='daily'):
        return "OBV", 'Technical Analysis: OBV', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ht_trendline(self, interval='daily', series_type='close'):
        return "HT_TRENDLINE", 'Technical Analysis: HT_TRENDLINE', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ht_sine(self, interval='daily', series_type='close'):
        return "HT_SINE", 'Technical Analysis: HT_SINE', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ht_trendmode(self, interval='daily', series_type='close'):
        return "HT_TRENDMODE", 'Technical Analysis: HT_TRENDMODE', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ht_dcperiod(self, interval='daily', series_type='close'):
        return "HT_DCPERIOD", 'Technical Analysis: HT_DCPERIOD', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ht_dcphase(self, interval='daily', series_type='close'):
        return "HT_DCPHASE", 'Technical Analysis: HT_DCPHASE', 'Meta Data'

    @output_format_av
    @call_api_on_func
    def get_ht_phasor(self, interval='daily', series_type='close'):
        return "HT_PHASOR", 'Technical Analysis: HT_PHASOR', 'Meta Data'
