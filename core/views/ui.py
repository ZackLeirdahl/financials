from tkinter import *
import configs as c
import os,sys,inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
from iex import StockReader
from robinhood import Robinhood

class View:
    def __init__(self, title, fields):
        self.root = Tk()
        self.root.title(title)
        self.entries = {}
        self.fields = fields

    def build_entries(self):
        for field in self.fields:
            row = Frame(self.root)
            label = Label(row, width=15, text=field, anchor='w')
            entry = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            label.pack(side=LEFT)
            entry.pack(side=RIGHT, expand=YES, fill=X)
            self.entries[field] = entry

    def start(self):
        raise NotImplementedError('This is overridden in child class.')

    def refresh(self, data):

class StockView(View):
    def __init__(self, title, fields):
        View.__init__(self, title, fields)
        self.execute = Button(self.root,text='Execute',command=self.update)

    def start(self):
        self.build_entries()
        self.execute.pack(side=LEFT, padx=5, pady=5)
        self.root.mainloop()

    def update(self):
        s = StockReader([self.entries['Symbol'].get()])
        data = s.get_overview()
        for k,v in data.items():
            self.entries[k].insert(0,v)

#This view can import options and run theoretical scenarios
class OptionView(View):
    def __init__(self, title, fields):
        View.__init__(self, title, fields)

class UnuasualOptionView(View):
    def __init__(self, title, fields):
        View.__init__(self, title, fields)
        self.execute = Button(self.root,text='Execute',command=self.update)

    def start(self):
        self.build_entries()
        self.execute.pack(side=LEFT, padx=5, pady=5)
        self.root.mainloop()

    def update(self):
        r = Robinhood()
        data = r.get_highest_volume_strike(self.entries['Symbol'].get(),int(self.entries['Number of Weeks'].get()),self.entries['Type'].get().lower())
        for k,v in data.items():
            self.entries[k].insert(0,v)


if __name__ == '__main__':
    params = c.get_params('UnuasualOptionView')
    #app = StockView(params['Title'],params['Fields'])
    app = UnuasualOptionView(params['Title'],params['Fields'])
    app.start()
