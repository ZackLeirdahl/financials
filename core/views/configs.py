
def get_params(view):
    params = {
        'Stock View': {
            'title':'Stock Overview',
            'fields': ['Symbol','Price','Volume','Average Volume','VWAP','High','Low']},
        'UnuasualOptionView': {
            'title': 'Unuasual Option View',
            'fields': ['Symbol', 'Number of Weeks','Type', 'Expiration', 'Strike', 'Mark', 'Volume', 'Open Interest']}}
    return params[view]
