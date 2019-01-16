from robinhood import Robinhood
from option import Option
from iex import StockReader
class Position:
    def __init__(self, args):
        self.args = args
        self._ticker_symbol = None
        self._id = None
        self._type = None
        self._url = None
        self._mark = None
        self._equity = None
        self._cost = None
        self._quantity = None
        self._return_dollar = None
        self._return_percentage = None
        self._data = None

    @property
    def ticker_symbol(self):
        self._ticker_symbol = self.args['ticker_symbol']
        return self._ticker_symbol

    @property
    def id(self):
        self._id = self.args['id']
        return self._id

    @property
    def type(self):
        self._type = self.args['type']
        return self._type

    @property
    def url(self):
        self._url = self.args['url']
        return self._url

    @property
    def mark(self):
        self._mark = self.args['mark']
        return self._mark

    @property
    def quantity(self):
        self._quantity = int(float(self.args['quantity']))
        return self._quantity

    @property
    def cost(self):
        self._cost = round(float(self.args['average_cost']) * self.quantity,2)
        return self._cost

    @property
    def equity(self):
        self._equity = self.quantity * self.mark
        return self._equity

    @property
    def return_dollar(self):
        self._return_dollar = round(self.equity - self.cost,2)
        return self._return_dollar

    @property
    def return_percentage(self):
        self._return_percentage = round((((self.equity / self.cost)-1) * 100),2)
        return self._return_percentage

    @property
    def data(self):
        self._data = {p: getattr(self, p) for p in self._properties}
        return self._data

    _properties = ['ticker_symbol', 'id', 'type', 'url', 'cost', 'quantity', 'equity', 'return_dollar', 'return_percentage']

class Positions(Robinhood):
    def __init__(self):
        Robinhood.__init__(self)

    def get_security_positions(self, results = []):
        data = self.securities_owned()
        for i in range(len(data)):
            instrument = self.get_url(data[i]['instrument'])
            reader = StockReader([instrument['symbol']])
            results.append({
                'average_cost': data[i]['average_buy_price'],
                'quantity': data[i]['quantity'],
                'url': data[i]['url'],
                'ticker_symbol': instrument['symbol'],
                'id': instrument['id'],
                'mark': reader.get_price(),
                'type': 'security'
            })
        return results

    def get_option_positions(self, results = []):
        data = self.get_options_positions()
        for i in range(len(data)):
            market_data = self.get_option_market_data(data[i]['option'][:-1].split('/')[-1])
            results.append({
                'average_cost': data[i]['average_price'],
                'quantity' : data[i]['quantity'],
                'url': data[i]['url'],
                'ticker_symbol': data[i]['chain_symbol'],
                'id': data[i]['id'],
                'mark': float(market_data['mark_price']) * 100,
                'type': 'option'
            })
        return results
