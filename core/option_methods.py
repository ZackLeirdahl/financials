from client import APIClient

class OptionMethods(APIClient):
    def __init__(self, symbol, weeks = 4):
        APIClient.__init__(self,symbol)
        self.call_chain = self.get_options(weeks,'call')
        self.put_chain = self.get_options(weeks,'put')
        self.contracts = self.call_chain+ self.put_chain
        self.call_volume = self.get_option_volume_call()
        self.put_volume = self.get_option_volume_put()
        self.volume = self.call_volume + self.put_volume
        self.open_interest_call = self.get_open_interest_call()
        self.open_interest_put = self.get_open_interest_put()
        self.open_interest = self.open_interest_call + self.open_interest_put
        self.spread = self.call_volume/(self.call_volume+self.put_volume)
        self.highest_volume_call = self.get_highest_volume_call()
        self.highest_volume_put = self.get_highest_volume_put()

    def get_highest_volume_call(self):
        mkt_data = self.get_option_market_data(sorted({option['id']:self.get_option_market_data(option['id'])['volume'] for option in self.call_chain}.items(),key=lambda kv: kv[1],reverse=True)[0][0])
        inst = self.get_url(mkt_data['instrument'])
        return {'Expiration': inst['expiration_date'], 'Strike': inst['strike_price'], 'Mark': mkt_data['mark_price'], 'Volume': mkt_data['volume'], 'Open Interest': mkt_data['open_interest']}

    def get_highest_volume_put(self):
        mkt_data = self.get_option_market_data(sorted({option['id']:self.get_option_market_data(option['id'])['volume'] for option in self.put_chain}.items(),key=lambda kv: kv[1],reverse=True)[0][0])
        inst = self.get_url(mkt_data['instrument'])
        return {'Expiration': inst['expiration_date'], 'Strike': inst['strike_price'], 'Mark': mkt_data['mark_price'], 'Volume': mkt_data['volume'], 'Open Interest': mkt_data['open_interest']}

    def get_open_interest_call(self):
        return sum([int(self.get_option_market_data(option['id'])['open_interest']) for option in self.call_chain])

    def get_open_interest_put(self):
        return sum([int(self.get_option_market_data(option['id'])['open_interest']) for option in self.put_chain])

    def get_option_volume_call(self):
        return sum([int(self.get_option_market_data(option['id'])['volume']) for option in self.call_chain])

    def get_option_volume_put(self):
        return sum([int(self.get_option_market_data(option['id'])['volume']) for option in self.put_chain])

    def get_data(self):
        return {'call_volume':self.call_volume, 'put_volume':self.put_volume, 'volume': self.volume, 'call_open_interest': self.open_interest_call, 'put_open_interest': self.open_interest_put, 'open_interest': self.open_interest, 'spread': self.spread, 'highest_volume_call': self.highest_volume_call, 'highest_volume_put': self.highest_volume_put}

o = OptionMethods('bac')
print(o.get_data())
