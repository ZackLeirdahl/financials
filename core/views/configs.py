
def get_params(view):
    params = {
        'StockView': {
            'Title':'Stock Overview',
            'Fields': ['Symbol','Price','Volume','Average Volume','VWAP','MA(10)','MA(20)','MA(50)','Open','High','Low','Close']},
        'OptionView': {
            'Title': 'Option View',
            'Fields': ['ID','Symbol','Type', 'Expiration', 'Strike', 'Implied Volatility', 'Interest Rate', 'Mark', 'Theoretical Mark']},
        'UnuasualOptionView': {
            'Title': 'Unuasual Option View',
            'Fields': ['Symbol', 'Number of Weeks','Type', 'Expiration', 'Strike', 'Mark', 'Volume', 'Open Interest']}}
    return params[view]
