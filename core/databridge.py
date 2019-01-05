from firebase import Firebase
from stock import Stock
from option import Option
from positions import OptionPositions

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
