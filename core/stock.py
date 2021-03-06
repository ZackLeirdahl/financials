from methods import ClientMethods

class Stock(ClientMethods):
    def __init__(self, symbol):
        ClientMethods.__init__(self, symbol)
        self.ticker_symbol = symbol.upper()
        self._name = None
        self._sector = None
        self._industry = None
        self._exchange = None
        self._historical_volatility = None
        self._beta = None
        self._short_date = None
        self._short_interest = None
        self._market_cap = None
        self._shares_outstanding = None
        self._data = None

    @property
    def name(self):
    	self._name = self.get_company()['companyName']
    	return self._name

    @property
    def sector(self):
    	self._sector = self.get_company()['sector']
    	return self._sector

    @property
    def industry(self):
    	self._industry = self.get_company()['industry']
    	return self._industry

    @property
    def exchange(self):
    	self._exchange = self.get_company()['exchange']
    	return self._exchange

    @property
    def beta(self):
    	self._beta = round(self.get_key_stats()['beta'], 2)
    	return self._beta

    @property
    def historical_volatility(self):
        self._historical_volatility = self.get_historical_volatility()
        return self._historical_volatility

    @property
    def short_date(self):
        self._short_date = self.get_key_stats()['shortDate']
        return self._short_date

    @property
    def short_interest(self):
        self._short_date = self.get_key_stats()['shortInterest']
        return self._short_interest

    @property
    def shares_outstanding(self):
    	self._shares_outstanding = self.get_key_stats()['sharesOutstanding']
    	return self._shares_outstanding

    @property
    def market_cap(self):
    	self._market_cap = self.get_key_stats()['marketcap']
    	return self._market_cap

    @property
    def data(self):
        self._data = {p: getattr(self, p) for p in self._properties}
        return self._data

    _properties =  ['name','sector','industry','exchange','beta','short_date','short_interest','shares_outstanding','market_cap','historical_volatility']
