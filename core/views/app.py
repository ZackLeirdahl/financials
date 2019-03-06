import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from configs import *
from ui import StockView
class Application(Frame):

    views = ['Stock View', 'Unusual Option View']

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.build_view()
        self.mainloop()

    def build_view(self):
        self.selections = Combobox(self, values=self.views)
        self.toggle = Button(self, text='Go',command = self.toggle_view)
        self.selections.pack()
        self.toggle.pack()

    def toggle_view(self):
        params = get_params(self.selections.get())
        app = StockView(params['title'],params['fields'])
        app.start()


if __name__ == '__main__':
    root = Tk()
    app = Application(master = root)
