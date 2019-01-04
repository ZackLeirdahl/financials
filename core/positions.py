from robinhood import Robinhood
from option import Option

class OptionPositions(Robinhood):
    def __init__(self):
        Robinhood.__init__(self)
        self.options = [Option(self.get_url(position)) for position in self.get_options_positions()]

    def get_records(self):
        #schema = option_positions/id/data
        return {option.id : option.data for option in self.options}


class SecurityPositions(Robinhood):
    def __init__(self):
        Robinhood.__init__(self)

    def get_security_positions(self):
        data = self.securities_owned()
        for position in data:
            return
            #get the data for each position and from the instrument, do a self.get_url for the instrument
