from iex import StockReader
from robinhood import Robinhood
<<<<<<< HEAD
<<<<<<< HEAD
from option import Option

#VWAP 1 Day = (Sum of number of shares bought * price) / number of shares bought
# s = StockReader(['NFLX'])
# chart = s.get_chart(range='1d')
# vw = 0
# volume = 0
# for point in chart:
#     avg = float(point['marketAverage'])
#     vol = float(point['marketVolume'])
#     vw += avg * vol
#     volume += vol
# vwap = vw/volume
#######################

#Find highest_volume for option chain
r = Robinhood()
volume = 0
highest_volume = None
for option in r.get_options('NFLX',['2019-01-18','2019-01-25'],'call'):
    temp_vol = r.get_option_market_data(option['id'])['volume']
    if temp_vol > volume:
        volume = temp_vol
        highest_volume = option
###################################
=======
=======
import numpy as np
from datetime import *
from math import *
>>>>>>> eeb668488f0764af353528f4ad60e94b2b0fab42

def get_theoretical_mark(strike, price, imp_vol, expiration_date, option_type = 'call', interest_rate= 0.025):
    maturity_time = (date.fromordinal(datetime.strptime(expiration_date,'%Y-%m-%d').toordinal()) - date.today()).days / 365
    d1 = (np.log(price / strike) + (interest_rate + 0.5 * imp_vol ** 2) * maturity_time) / (imp_vol * np.sqrt(maturity_time))
    d2 = (np.log(price / strike) + (interest_rate - 0.5 * imp_vol ** 2) * maturity_time) / (imp_vol * np.sqrt(maturity_time))
    options = {'call':(price * cumulative_normal_dist(d1) - strike * np.exp(-interest_rate * maturity_time) * cumulative_normal_dist(d2)), 'put': (strike * np.exp(-interest_rate * maturity_time) * cumulative_normal_dist(-d2) - price * cumulative_normal_dist(-d1))}
    return options[option_type]

<<<<<<< HEAD
def get_highest_volume(ticker_symbol, dates, type, volume = 0, highest_volume = None):
    r = Robinhood()
    for option in r.get_options(ticker_symbol, dates, type):
        temp_vol = r.get_option_market_data(option['id'])['volume']
        if temp_vol > volume:
            volume = temp_vol
            highest_volume = option
    return highest_volume
>>>>>>> 02a2149dd3309fd41580b145047b2a4667b1c649
=======
def cumulative_normal_dist(derivative):
    dist = 1-1/sqrt(2*pi)*exp(-abs(derivative)*abs(derivative)/2.)*(0.31938153*(1.0/(1.0+0.2316419* abs(derivative)))+-0.356563782*(1.0/(1.0+0.2316419* abs(derivative)))*(1.0/(1.0+0.2316419* abs(derivative)))+1.781477937*pow((1.0/(1.0+0.2316419* abs(derivative))),3)+-1.821255978*pow((1.0/(1.0+0.2316419* abs(derivative))),4)+1.330274429*pow((1.0/(1.0+0.2316419* abs(derivative))),5))
    if derivative < 0: return 1-dist
    return dist

#print(get_theoretical_mark(60,50.22,.75,'2019-02-15'))
>>>>>>> eeb668488f0764af353528f4ad60e94b2b0fab42
