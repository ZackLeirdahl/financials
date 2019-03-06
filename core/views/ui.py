from tkinter import *
from configs import *
import os, sys, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\interfaces')
from utils import *
from methods import StockMethods

class BaseView(StockMethods):
    def __init__(self, title, fields):
        StockMethods.__init__(self,'')
        self.root = Tk()
        self.root.title(title)
        self.entries = {}
        self.fields = fields
        self.build_entries()

    def build_entries(self):
        for field in self.fields:
            row = Frame(self.root)
            label = Label(row, width=15, text=field, anchor='w')
            entry = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            label.pack(side=LEFT)
            entry.pack(side=RIGHT, expand=YES, fill=X)
            self.entries[field] = entry

    def refresh(self, data):
        for k,v in data.items():
            self.entries[k].delete(0,END)
            self.entries[k].insert(0,v)

    def start(self):
        raise NotImplementedError('This is definied in child class.')

    def update(self):
        raise NotImplementedError('This is definied in child class.')

class StockView(BaseView):
    def __init__(self, title, fields):
        BaseView.__init__(self, title, fields)
        self.execute_text = StringVar(self.root,value='Execute')
        self.execute = Button(self.root, textvariable=self.execute_text,command=self.update)
        self.format_price = False

    def start(self):
        self.execute.pack(side=LEFT,padx=5,pady=5)
        self.root.mainloop()

    def update(self):
        self.symbol = self.entries['Symbol'].get().upper()
        if self.execute_text.get() == 'Execute':
            self.execute_text.set('Format Percent')
            self.format_price = True
        else:
            self.execute_text.set('Execute')
            self.format_price = False
        self.refresh(self.get_overview(self.format_price))

class UnuasualOptionView(BaseView):
    def __init__(self, title, fields):
        BaseView.__init__(self, title, fields)

    def update(self):
        self.symbol = self.entries['Symbol'].get().upper()
        self.refresh(self.get_highest_volume_strike(int(self.entries['Number of Weeks'].get()),self.entries['Type'].get().lower()))


if __name__ == '__main__':
    params = get_params('Stock View')
    app = StockView(params['title'],params['fields'])
    app.start()
