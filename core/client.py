import requests
from utils import *
from const import api_base, authorizations, robinhood_headers
class Client(object):
    def __init__(self, symbol=None, output_format='pandas', **kwargs):
        self.symbol = symbol.upper()
        self.output_format = output_format
        self.iex_session = None
        self.robinhood_session = None
        self.headers = robinhood_headers

    def login(self):
        if self.robinhood_session == None:
            self.robinhood_session = requests.session()
            self.robinhood_session.headers = self.headers
        self.headers['Authorization'] = 'Bearer ' + self.robinhood_session.post(token(), data=authorizations['robinhood'], timeout=15).json()['access_token']

    def _execute_iex_query(self):
        if self.iex_session == None: self.iex_session = requests.session()
        for i in range(5): return self.iex_session.get(url=api_base['iex'], params=self.params).json(parse_int=None, parse_float=None)

    @property
    def params(self):
        temp = {'symbols': self.symbol, 'types': ','.join(self.endpoints)}
        temp.update({k: v for k, v in self.optional_params.items()})
        if 'filter_' in temp:
            if isinstance(temp['filter_'], list): temp['filter'] = ','.join(temp.pop('filter_'))
            else: temp['filter'] = temp.pop('filter_')
        params = {k: str(v).lower() if v is True or v is False else str(v) for k, v in temp.items()}
        return params

    def _get_endpoint(self, endpoint, params={}):
        self.optional_params = params
        self.endpoints = [endpoint]
        return self._execute_iex_query()

    def get_chart(self, **kwargs):
        return self._get_endpoint('chart', kwargs)[self.symbol]['chart']

    def get_company(self, **kwargs):
        return self._get_endpoint('company', kwargs)[self.symbol]['company']

    def get_earnings(self, **kwargs):
        return self._get_endpoint('earnings', kwargs)[self.symbol]['earnings']['earnings']

    def get_financials(self, **kwargs):
        return self._get_endpoint('financials', kwargs)[self.symbol]['financials']['financials']

    def get_key_stats(self, **kwargs):
        return self._get_endpoint('stats', kwargs)[self.symbol]['stats']

    def get_largest_trades(self, **kwargs):
        return self._get_endpoint('largest-trades', kwargs)['largest-trades']

    def get_ohlc(self, **kwargs):
        return self._get_endpoint('ohlc', kwargs)[self.symbol]['ohlc']

    def get_price(self, **kwargs):
        return self._get_endpoint('price', kwargs)[self.symbol]['price']

    def get_quote(self, **kwargs):
        return self._get_endpoint('quote', kwargs)[self.symbol]['quote']

    def get_volume(self):
        return self.get_quote(filter_='latestVolume')['latestVolume']

    @login_required
    def instruments(self):
        return self.robinhood_session.get(instruments(), params={'query': self.symbol}, timeout=15).json()['results']

    @login_required
    def instrument(self, id):
        return requests.get(str(instruments()) + str(id) + '/', timeout=15).json()

    @login_required
    def get_url(self, url):
        return self.robinhood_session.get(url, timeout=15).json()

    @login_required
    def get_tickers_by_tag(self, tag=None):
        return [self.get_url(instrument)['symbol'] for instrument in self.get_url(tags(tag))['instruments']]

    @login_required
    def get_options(self, weeks, option_type):
        return [contract for contract in self.get_url(options(self.get_url(chain(self.instruments()[0]['id']))['results'][0]['id'], get_dates(weeks), option_type))['results']]

    @login_required
    def get_option_market_data(self, optionid):
        return self.get_url(market_data(optionid))

    @login_required
    def get_options_positions(self):
        return list(filter(lambda k: float(k['quantity']) > 0, self.robinhood_session.get(option_positions(),timeout=15).json()['results']))

    @output_format
    @api_call
    def get_intraday(self, interval='15min', outputsize='compact'):
        return 'TIME_SERIES_INTRADAY', 'Time Series ({})'.format(interval), 'Meta Data'

    @output_format
    @api_call
    def get_intraday(self, interval='15min', outputsize='compact'):
        return 'TIME_SERIES_INTRADAY', 'Time Series ({})'.format(interval), 'Meta Data'

    @output_format
    @api_call
    def get_daily(self, outputsize='compact'):
        return 'TIME_SERIES_DAILY', 'Time Series (Daily)', 'Meta Data'

    @output_format
    @api_call
    def get_daily_adjusted(self, outputsize='compact'):
        return 'TIME_SERIES_DAILY_ADJUSTED', 'Time Series (Daily)', 'Meta Data'

    @output_format
    @api_call
    def get_weekly(self):
        return 'TIME_SERIES_WEEKLY', 'Weekly Time Series', 'Meta Data'

    @output_format
    @api_call
    def get_weekly_adjusted(self):
        return 'TIME_SERIES_WEEKLY_ADJUSTED', 'Weekly Adjusted Time Series', 'Meta Data'

    @output_format
    @api_call
    def get_monthly(self):
        return 'TIME_SERIES_MONTHLY', 'Monthly Time Series', 'Meta Data'

    @output_format
    @api_call
    def get_monthly_adjusted(self):
        return 'TIME_SERIES_MONTHLY_ADJUSTED', 'Monthly Adjusted Time Series', 'Meta Data'

    @output_format
    @api_call
    def get_sma(self, interval='daily', time_period=20, series_type='close'):
        return 'SMA', 'Technical Analysis: SMA', 'Meta Data'

    @output_format
    @api_call
    def get_ema(self, interval='daily', time_period=20, series_type='close'):
        return 'EMA', 'Technical Analysis: EMA', 'Meta Data'

    @output_format
    @api_call
    def get_wma(self, interval='daily', time_period=20, series_type='close'):
        return 'WMA', 'Technical Analysis: WMA', 'Meta Data'

    @output_format
    @api_call
    def get_dema(self, interval='daily', time_period=20, series_type='close'):
        return 'DEMA', 'Technical Analysis: DEMA', 'Meta Data'

    @output_format
    @api_call
    def get_tema(self, interval='daily', time_period=20, series_type='close'):
        return 'TEMA', 'Technical Analysis: TEMA', 'Meta Data'

    @output_format
    @api_call
    def get_trima(self, interval='daily', time_period=20, series_type='close'):
        return 'TRIMA', 'Technical Analysis: TRIMA', 'Meta Data'

    @output_format
    @api_call
    def get_kama(self, interval='daily', time_period=20, series_type='close'):
        return 'KAMA', 'Technical Analysis: KAMA', 'Meta Data'

    @output_format
    @api_call
    def get_mama(self, interval='daily', series_type='close', fastlimit=None, slowlimit=None):
        return 'MAMA', 'Technical Analysis: MAMA', 'Meta Data'

    @output_format
    @api_call
    def get_t3(self, interval='daily', time_period=20, series_type='close'):
        return 'T3', 'Technical Analysis: T3', 'Meta Data'

    @output_format
    @api_call
    def get_macd(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, signalperiod=None):
        return 'MACD', 'Technical Analysis: MACD', 'Meta Data'

    @output_format
    @api_call
    def get_macdext(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, signalperiod=None, fastmatype=None, slowmatype=None, signalmatype=None):
        return 'MACDEXT', 'Technical Analysis: MACDEXT', 'Meta Data'

    @output_format
    @api_call
    def get_stoch(self, interval='daily', fastkperiod=None, slowkperiod=None, slowdperiod=None, slowkmatype=None, slowdmatype=None):
        return 'STOCH', 'Technical Analysis: STOCH', 'Meta Data'

    @output_format
    @api_call
    def get_stochf(self, interval='daily', fastkperiod=None, fastdperiod=None, fastdmatype=None):
        return 'STOCHF', 'Technical Analysis: STOCHF', 'Meta Data'

    @output_format
    @api_call
    def get_rsi(self, interval='daily', time_period=20, series_type='close'):
        return 'RSI', 'Technical Analysis: RSI', 'Meta Data'

    @output_format
    @api_call
    def get_stochrsi(self, interval='daily', time_period=20, series_type='close', fastkperiod=None, fastdperiod=None, fastdmatype=None):
        return 'STOCHRSI', 'Technical Analysis: STOCHRSI', 'Meta Data'

    @output_format
    @api_call
    def get_willr(self, interval='daily', time_period=20):
        return 'WILLR', 'Technical Analysis: WILLR', 'Meta Data'

    @output_format
    @api_call
    def get_adx(self, interval='daily', time_period=20):
        return 'ADX', 'Technical Analysis: ADX', 'Meta Data'

    @output_format
    @api_call
    def get_adxr(self, interval='daily', time_period=20):
        return 'ADXR', 'Technical Analysis: ADXR', 'Meta Data'

    @output_format
    @api_call
    def get_apo(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, matype=None):
        return 'APO', 'Technical Analysis: APO', 'Meta Data'

    @output_format
    @api_call
    def get_ppo(self, interval='daily', series_type='close', fastperiod=None, slowperiod=None, matype=None):
        return 'PPO', 'Technical Analysis: PPO', 'Meta Data'

    @output_format
    @api_call
    def get_mom(self, interval='daily', time_period=20, series_type='close'):
        return 'MOM', 'Technical Analysis: MOM', 'Meta Data'

    @output_format
    @api_call
    def get_bop(self, interval='daily', time_period=20):
        return 'BOP', 'Technical Analysis: BOP', 'Meta Data'

    @output_format
    @api_call
    def get_cci(self, interval='daily', time_period=20):
        return 'CCI', 'Technical Analysis: CCI', 'Meta Data'

    @output_format
    @api_call
    def get_cmo(self, interval='daily', time_period=20, series_type='close'):
        return 'CMO', 'Technical Analysis: CMO', 'Meta Data'

    @output_format
    @api_call
    def get_roc(self, interval='daily', time_period=20, series_type='close'):
        return 'ROC', 'Technical Analysis: ROC', 'Meta Data'

    @output_format
    @api_call
    def get_rocr(self, interval='daily', time_period=20, series_type='close'):
        return 'ROCR', 'Technical Analysis: ROCR', 'Meta Data'

    @output_format
    @api_call
    def get_aroon(self, interval='daily', time_period=20, series_type='close'):
        return 'AROON', 'Technical Analysis: AROON', 'Meta Data'

    @output_format
    @api_call
    def get_aroonosc(self, interval='daily', time_period=20, series_type='close'):
        return 'AROONOSC', 'Technical Analysis: AROONOSC', 'Meta Data'

    @output_format
    @api_call
    def get_mfi(self, interval='daily', time_period=20, series_type='close'):
        return 'MFI', 'Technical Analysis: MFI', 'Meta Data'

    @output_format
    @api_call
    def get_trix(self, interval='daily', time_period=20, series_type='close'):
        return 'TRIX', 'Technical Analysis: TRIX', 'Meta Data'

    @output_format
    @api_call
    def get_ultsoc(self, interval='daily', timeperiod1=None, timeperiod2=None, timeperiod3=None):
        return 'ULTOSC', 'Technical Analysis: ULTOSC', 'Meta Data'

    @output_format
    @api_call
    def get_dx(self, interval='daily', time_period=20, series_type='close'):
        return 'DX', 'Technical Analysis: DX', 'Meta Data'

    @output_format
    @api_call
    def get_minus_di(self, interval='daily', time_period=20):
        return 'MINUS_DI', 'Technical Analysis: MINUS_DI', 'Meta Data'

    @output_format
    @api_call
    def get_plus_di(self, interval='daily', time_period=20):
        return 'PLUS_DI', 'Technical Analysis: PLUS_DI', 'Meta Data'

    @output_format
    @api_call
    def get_minus_dm(self, interval='daily', time_period=20):
        return 'MINUS_DM', 'Technical Analysis: MINUS_DM', 'Meta Data'

    @output_format
    @api_call
    def get_plus_dm(self, interval='daily', time_period=20):
        return 'PLUS_DM', 'Technical Analysis: PLUS_DM', 'Meta Data'

    @output_format
    @api_call
    def get_bbands(self, interval='daily', time_period=20,  series_type='close', nbdevup=None, nbdevdn=None, matype=None):
        return 'BBANDS', 'Technical Analysis: BBANDS', 'Meta Data'

    @output_format
    @api_call
    def get_midpoint(self, interval='daily', time_period=20, series_type='close'):
        return 'MIDPOINT', 'Technical Analysis: MIDPOINT', 'Meta Data'

    @output_format
    @api_call
    def get_midprice(self, interval='daily', time_period=20):
        return 'MIDPRICE', 'Technical Analysis: MIDPRICE', 'Meta Data'

    @output_format
    @api_call
    def get_sar(self, interval='daily', acceleration=None, maximum=None):
        return 'SAR', 'Technical Analysis: SAR', 'Meta Data'

    @output_format
    @api_call
    def get_trange(self, interval='daily'):
        return 'TRANGE', 'Technical Analysis: TRANGE', 'Meta Data'

    @output_format
    @api_call
    def get_atr(self, interval='daily', time_period=20):
        return 'ATR', 'Technical Analysis: ATR', 'Meta Data'

    @output_format
    @api_call
    def get_natr(self, interval='daily', time_period=20):
        return 'NATR', 'Technical Analysis: NATR', 'Meta Data'

    @output_format
    @api_call
    def get_ad(self, interval='daily'):
        return 'AD', 'Technical Analysis: Chaikin A/D', 'Meta Data'

    @output_format
    @api_call
    def get_adosc(self, interval='daily', fastperiod=None, slowperiod=None):
        return 'ADOSC', 'Technical Analysis: ADOSC', 'Meta Data'

    @output_format
    @api_call
    def get_obv(self, interval='daily'):
        return 'OBV', 'Technical Analysis: OBV', 'Meta Data'

    @output_format
    @api_call
    def get_ht_trendline(self, interval='daily', series_type='close'):
        return 'HT_TRENDLINE', 'Technical Analysis: HT_TRENDLINE', 'Meta Data'

    @output_format
    @api_call
    def get_ht_sine(self, interval='daily', series_type='close'):
        return 'HT_SINE', 'Technical Analysis: HT_SINE', 'Meta Data'

    @output_format
    @api_call
    def get_ht_trendmode(self, interval='daily', series_type='close'):
        return 'HT_TRENDMODE', 'Technical Analysis: HT_TRENDMODE', 'Meta Data'

    @output_format
    @api_call
    def get_ht_dcperiod(self, interval='daily', series_type='close'):
        return 'HT_DCPERIOD', 'Technical Analysis: HT_DCPERIOD', 'Meta Data'

    @output_format
    @api_call
    def get_ht_dcphase(self, interval='daily', series_type='close'):
        return 'HT_DCPHASE', 'Technical Analysis: HT_DCPHASE', 'Meta Data'

    @output_format
    @api_call
    def get_ht_phasor(self, interval='daily', series_type='close'):
        return 'HT_PHASOR', 'Technical Analysis: HT_PHASOR', 'Meta Data'
