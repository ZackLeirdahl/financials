from robinhood import Robinhood
import calculations as calcs
class Option(Robinhood):
    def __init__(self, args):
        Robinhood.__init__(self)
        if type(args) == dict: self.args = args
        else: self.args = self.get_url(args)
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
        self._mark = self.details['mark_price']
        return self._mark

    @property
    def open_interest(self):
        self._open_interest = self.details['open_interest']
        return self._open_interest

    @property
    def volume(self):
        self._volume = self.details['volume']
        return self._volume

    @property
    def implied_volatility(self):
        self._implied_volatility = round(float(self.details['implied_volatility']),3)
        return self._implied_volatility

    @property
    def delta(self):
        self._delta = self.details['delta']
        return self._delta

    @property
    def gamma(self):
        self._gamma = self.details['gamma']
        return self._gamma

    @property
    def theta(self):
        self._theta = self.details['theta']
        return self._theta

    @property
    def theoretical_mark(self):
        self._theoretical_mark = calcs.get_theoretical_mark(self.ticker_symbol, self.strike, self.implied_volatility, self.expiration, self.type)
        return self._theoretical_mark

    @property
    def data(self):
        self.details = self.get_option_market_data(self.id)
        self._data = {p: getattr(self, p) for p in self._properties}
        return self._data

    _properties =  ['type','expiration','strike','mark','implied_volatility','open_interest','volume','delta','gamma','theta','theoretical_mark']
