
def get_params(view):
    params = {
        'StockView': {
            'Title':'Stock Overview',
            'Fields': ['Symbol','Price','Volume','Average Volume','VWAP','MA(10)','MA(50)','MA(200)','Open','High','Low','Close']},
        'OptionView': {
            'Title': 'Option View',
            'Fields': ['ID','Symbol','Type', 'Expiration', 'Strike', 'Implied Volatility', 'Interest Rate', 'Mark', 'Theoretical Mark']}}
    return params[view]
