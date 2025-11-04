"""Tk version of the CwcTopLevel, used by panels that need transparent frames (PopupMenu)"""

import tkinter as tk
from tkinter import ttk

from cwc_globals import set_window_to_mouse_point_tk

class CwcTopLevel(tk.Toplevel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.overrideredirect(True)

        self.bind('<Escape>', self.quit)

    def show(self):
        self.__position_win()
        self.lift()
        self.grab_set()
        self.wait_window()

    def quit(self, _='', __=''):
        self.destroy()
        self.update()

    def __position_win(self):
        set_window_to_mouse_point_tk(win=self)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    set_style()

    window = CwcTopLevel()
    window.geometry('500x100')
    ttk.Label(master=window, text="just a test 1").pack(padx=10, pady=2)
    ttk.Label(master=window, text="just a test 2").pack(padx=10, pady=2)
    ttk.Label(master=window, text="just a test 3").pack(padx=10, pady=2)
    ttk.Label(master=window, text="just a test 4").pack(padx=10, pady=2)
    window.show()
