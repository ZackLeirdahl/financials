
def get_params(view):
    params = {
        'Stock View': {
            'title':'Stock Overview',
            'fields': ['Symbol','Price','Volume','Average Volume','VWAP','MA(10)','MA(20)','MA(50)','High','Low']},
        'UnuasualOptionView': {
            'title': 'Unuasual Option View',
            'fields': ['Symbol', 'Number of Weeks','Type', 'Expiration', 'Strike', 'Mark', 'Volume', 'Open Interest']}}
    return params[view]
