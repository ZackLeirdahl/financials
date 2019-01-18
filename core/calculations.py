from iex import StockReader
from robinhood import Robinhood
import numpy as np
from datetime import *
from math import *

def get_vwap_daily(ticker_symbol, vw = 0, volume = 0):
    s = StockReader([ticker_symbol])
    for point in s.get_chart(range='1d'):
        avg = float(point['marketAverage'])
        vol = float(point['marketVolume'])
        vw += avg * vol
        volume += vol
    return round(vw/volume,2)

def get_highest_volume(ticker_symbol, num_weeks = 2, type = 'call'):
    r = Robinhood()
    volume = 0
    highest_volume = None
    for option in r.get_options(ticker_symbol, get_dates(num_weeks), type):
        temp_vol = r.get_option_market_data(option['id'])['volume']
        if temp_vol > volume:
            volume = temp_vol
            highest_volume = option
    return highest_volume

def get_theoretical_mark(strike, price, imp_vol, expiration_date, option_type = 'call', interest_rate= 0.025):
    maturity_time = (date.fromordinal(datetime.strptime(expiration_date,'%Y-%m-%d').toordinal()) - date.today()).days / 365
    d1 = (np.log(price / strike) + (interest_rate + 0.5 * imp_vol ** 2) * maturity_time) / (imp_vol * np.sqrt(maturity_time))
    d2 = (np.log(price / strike) + (interest_rate - 0.5 * imp_vol ** 2) * maturity_time) / (imp_vol * np.sqrt(maturity_time))
    options = {'call':(price * cumulative_normal_dist(d1) - strike * np.exp(-interest_rate * maturity_time) * cumulative_normal_dist(d2)), 'put': (strike * np.exp(-interest_rate * maturity_time) * cumulative_normal_dist(-d2) - price * cumulative_normal_dist(-d1))}
    return options[option_type]

def cumulative_normal_dist(derivative):
    dist = 1-1/sqrt(2*pi)*exp(-abs(derivative)*abs(derivative)/2.)*(0.31938153*(1.0/(1.0+0.2316419* abs(derivative)))+-0.356563782*(1.0/(1.0+0.2316419* abs(derivative)))*(1.0/(1.0+0.2316419* abs(derivative)))+1.781477937*pow((1.0/(1.0+0.2316419* abs(derivative))),3)+-1.821255978*pow((1.0/(1.0+0.2316419* abs(derivative))),4)+1.330274429*pow((1.0/(1.0+0.2316419* abs(derivative))),5))
    if derivative < 0: return 1-dist
    return dist

def get_dates(num_weeks):
    #Add logic to give either month or num_weeks
    return [str(date.fromordinal(date.today().toordinal() + ((1+i)*{0:4,1:3,2:2,3:1,4:7,5:6,6:5}[date.today().weekday()]))) for i in range(num_weeks)]

#print(get_highest_volume('CGC',2,'call'))
#print(get_vwap_daily('CGC'))
#print(get_theoretical_mark(60,50.22,.75,'2019-02-15'))
