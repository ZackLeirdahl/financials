from firebase import Firebase
from stock import Stock
from option import Option, OptionPositions

class DataBridge(Firebase):
    def __init__(self):
        Firebase.__init__(self)

    def add_stock(self, ticker_symbol):
        stock = Stock(ticker_symbol)
        self.add_document('stocks',ticker_symbol,stock.data)

    def remove_stock(self, ticker_symbol):
        self.remove_document('stocks', ticker_symbol)

    def update_stock(self, ticker_symbol):
        stock = Stock(ticker_symbol)
        self.update_document('stocks',ticker_symbol, stock.data)

    def add_options_positions(self):
        positions = OptionPositions()
        records = positions.get_records()
        for k,v in records.items():
            self.add_document('positions', k, v)
