from option import Option
from robinhood import Robinhood

r = Robinhood()
pos = r.get_options_positions()
for i in range(len(pos)):
    o = Option(pos[i]['option'])
    print(o.data)
