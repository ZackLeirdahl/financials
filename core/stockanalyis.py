from stock import Stock
import pandas as pd

def get_moving_average(ticker_symbol, n):
    s = Stock(ticker_symbol)
    return round(list(pd.Series.rolling(pd.DataFrame(s.get_chart(range = '1y'))['close'], 50).mean())[-1],2)

def get_support(ticker_symbol, n):
    return

def get_resistance():
    return
