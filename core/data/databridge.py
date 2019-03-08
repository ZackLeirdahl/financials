from firebase import Firebase
from stock import Stock

class DataBridge(Firebase):
    def __init__(self):
        Firebase.__init__(self)

    def add_stock(self, ticker_symbol, collection = 'stocks'):
        stock = Stock(ticker_symbol)
        self.add_document(collection,ticker_symbol,stock.data)

    def remove_stock(self, ticker_symbol, collection = 'stocks'):
        self.remove_document(collection, ticker_symbol)

    def update_stock(self, ticker_symbol, collection = 'stocks'):
        stock = Stock(ticker_symbol)
        self.update_document(collection, ticker_symbol, stock.data)
