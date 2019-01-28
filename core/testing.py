from robinhood import Robinhood

r = Robinhood()
print(r.get_highest_volume_strike('AMD',1,'call'))
#print(r.get_option_market_data('7eac4691-074d-4fc7-8a7f-3812e198977c'))
