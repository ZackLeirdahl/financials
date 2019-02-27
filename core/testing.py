from option import Option
from robinhood import Robinhood

#calculate call/put spread
r = Robinhood()
data = r.get_options('sq',2,'call')
open_interest = 0
volume = 0
for option in data:
    o = r.get_option_market_data(option['id'])
    volume += int(o['volume'])
    open_interest += int(o['open_interest'])
#print(open_interest)
print(volume)
