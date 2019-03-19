
def get_params(view):
    params = {
        'Stock View': {
            'title':'Stock Overview',
            'fields': ['Symbol','Price','Volume','Average Volume','VWAP','High','Low']},
        'Option View': {
            'title': 'Option Overview',
            'fields': ['Symbol', 'Spread','Volume','Open Interest']
        }}
    return params[view]
