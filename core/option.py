from robinhood import Robinhood
class Option(Robinhood):
    def __init__(self, args):
        Robinhood.__init__(self)
        if type(args) == dict: self.args = args
        else: self.args = self.get_url("https://api.robinhood.com/options/instruments/" + args)
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

    @property
    def type(self):
        self._type = self.args['type']
        return self._type

    @property
    def strike(self):
        self._strike = self.args['strike_price']
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
        self._implied_volatility = self.details['implied_volatility']
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
    def data(self):
        self.details = self.get_option_market_data(self.id)
        self._data = {p: getattr(self, p) for p in self._properties}
        return self._data

    _properties =  ['type','expiration','strike','mark','implied_volatility','open_interest','volume','delta','gamma','theta']

class OptionPositions(Robinhood):
    def __init__(self):
        Robinhood.__init__(self)
        self.urls = self.get_options_positions()
        self.options = [Option(self.get_url(url)) for url in self.urls]

    def get_records(self):
        #schema = positions/id/data
        return {option.id : option.data for option in self.options}
