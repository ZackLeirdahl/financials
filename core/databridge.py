from firebase import Firebase
from stock import Stock
from option import Option
<<<<<<< HEAD
from positions import Position, Positions
=======
from positions import Positions
>>>>>>> eeb668488f0764af353528f4ad60e94b2b0fab42

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
<<<<<<< HEAD
        self.update_document('stocks',ticker_symbol, stock.data)

    def update_positions(self):
        p = Positions()
        positions = p.positions
        for position in positions:
            self.add_document('positions',position.id,position.data)

db = DataBridge()
db.update_positions()    
=======
        self.update_document(collection, ticker_symbol, stock.data)

    def update_positions(self, collection = 'positions'):
        p = Positions()
        previous_positions = self.get_documents(collection)
        new_positions = p.get_position_data()
        old_positions = list(set(previous_positions) - set(new_positions))
        for pos in old_positions: self.remove_document(collection, pos)
        for k, v in new_positions.items(): self.add_document(collection, k, v)
>>>>>>> eeb668488f0764af353528f4ad60e94b2b0fab42
