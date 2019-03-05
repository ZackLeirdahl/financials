from tkinter import *
from configs import *
import os, sys, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\interfaces')
from utils import *
from methods import StockMethods

class View(StockMethods):
    def __init__(self, title, fields):
        StockMethods.__init__(self, '')
        self.root = Tk()
        self.root.title(title)
        self.entries = {}
        self.fields = fields
        self.execute = Button(self.root,text='Execute',command=self.update)

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
        self.build_entries()
        self.execute.pack(side=LEFT, padx=5, pady=5)
        self.root.mainloop()

    def refresh(self, data):
        for k,v in data.items():
            self.entries[k].delete(0,END)
            self.entries[k].insert(0,v)

    def update(self):
        raise NotImplementedError('This is definied in child class.')

class StockView(View):
    def __init__(self, title, fields):
        View.__init__(self, title, fields)

    def update(self):
        self.symbol = self.entries['Symbol'].get().upper()
        self.refresh(self.get_overview())

class UnuasualOptionView(View):
    def __init__(self, title, fields):
        View.__init__(self, title, fields)

    def update(self):
        self.symbol = self.entries['Symbol'].get().upper()
        self.refresh(self.get_highest_volume_strike(int(self.entries['Number of Weeks'].get()),self.entries['Type'].get().lower()))


if __name__ == '__main__':
    params = get_params('StockView')
    app = StockView(params['Title'],params['Fields'])
    app.start()
