"""Module to handle non blocking application's messages"""

from tkinter import ttk

from cwc_globals  import GlobalData
from cwc_toplevel import CwcTopLevel

class VolatileMessage:
    """Shows an auto closing window with a message.
    The auto closing time depends on the length of the message.
    """

    def __init__(self, text, center=False, auto_close=True, on_close=None):
        self.window = CwcTopLevel(center=center, bind_esc=False, focus=False)
        self.window.master.overrideredirect(True)
        self.window.master.attributes('-topmost', 'true')

        ttk.Label(
            master  = self.window.frame().master,
            text    = text,
            font    = (GlobalData.CURRENT_FONT_NAME, 14, 'bold'),
            padding = (5,0,5,0),
            style   = 'Volatile.TLabel').grid(row=0, column=0)

        if auto_close:
            self.window.master.after(1000 + 20 * len(text), self.window.quit)
            if on_close:
                on_close()

        self.window.show()


############# TESTS #############

if __name__ == '__main__':
    from cwc_style import set_style

    set_style()
    GlobalData.main_window.after(100, lambda :
        VolatileMessage(text='Prima esecuzione, sto inizializzando il database, per favore attendere...'))
    GlobalData.main_window.mainloop()
