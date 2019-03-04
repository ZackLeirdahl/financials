from api import StockReader
from utils import *

class Option(StockReader):
    def __init__(self, args):
        StockReader.__init__(self,symbol = '')
        self.args = self.build_args(args)
        self.symbol = self.args['chain_symbol']
        self.ticker_symbol = self.args['chain_symbol']
        self.id = self.args['id']
        self.details = None
        self._type = None
        self._strike = None
        self._expiration = None
        self._mark = None
        self._open_interest = None
        self._volume = None
        self._implied_volatility = None
        self._delta = None
        self._gamma = None
        self._theta = None
        self._data = None
        self._theoretical_mark = None

    def build_args(self, args):
        if type(args) == str:
            market_data = self.get_option_market_data(args)
            inst_data = self.get_url(market_data['instrument'])
        elif 'instrument' in args.keys():
            market_data = args
            inst_data =  self.get_url(market_data['instrument'])
        else:
            market_data = self.get_option_market_data(args['id'])
            inst_data = args
        market_data.update(inst_data)
        return {k: market_data[k] for k in ['volume','open_interest','implied_volatility','mark_price','delta','gamma','theta','chain_symbol','id','expiration_date','strike_price','type']}

    @property
    def type(self):
        self._type = self.args['type']
        return self._type

    @property
    def strike(self):
        self._strike = round(float(self.args['strike_price']),2)
        return self._strike

    @property
    def expiration(self):
        self._expiration = self.args['expiration_date']
        return self._expiration

    @property
    def mark(self):
        self._mark = self.args['mark_price']
        return self._mark

    @property
    def open_interest(self):
        self._open_interest = int(self.args['open_interest'])
        return self._open_interest

    @property
    def volume(self):
        self._volume = int(self.args['volume'])
        return self._volume

    @property
    def implied_volatility(self):
        self._implied_volatility = round(float(self.args['implied_volatility']),3)
        return self._implied_volatility

    @property
    def delta(self):
        self._delta = round(float(self.args['delta']),4)
        return self._delta

    @property
    def gamma(self):
        self._gamma = round(float(self.args['gamma']),4)
        return self._gamma

    @property
    def theta(self):
        self._theta = round(float(self.args['theta']),4)
        return self._theta

    @property
    def theoretical_mark(self):
        self._theoretical_mark = get_theoretical_mark(self.ticker_symbol, self.strike, self.implied_volatility, self.expiration, self.get_price(), self.type)
        return self._theoretical_mark

    @property
    def data(self):
        self.details = self.get_option_market_data(self.id)
        self._data = {p: getattr(self, p) for p in self._properties}
        return self._data

    _properties =  ['type','expiration','strike','mark','implied_volatility','open_interest','volume','delta','gamma','theta','theoretical_mark']
