"""Module to show about window."""

import os
import tkinter as tk

from PIL import Image, ImageTk

from cwc_globals  import GlobalData
from cwc_toplevel import CwcTopLevel
from cwc_button   import CwcButtonTkmt
from translations import gtbk


class About:
    def __init__(self) -> None:
        self.window = CwcTopLevel(focus=True)

        image    = Image.open(os.path.join(GlobalData.ROOT_DIR, 'images/cwc.jpg')).resize((128, 64))
        self.img = ImageTk.PhotoImage(image)

    def show(self):
        lf = self.window.frame().addLabelFrame(text=f" {gtbk('about')} ", row=0, col=0)
        lf.Label(text='', widgetkwargs={'image' : self.img})
        lf.Label(text='Crossword Creator', size=GlobalData.FONT_BIG_SIZE)
        lf.Label(text=gtbk('thanks_to'))
        lf.Label(text='• TKinterModernThemes (c) RobertJN64, MIT License', size=GlobalData.FONT_SMALL_SIZE, sticky=tk.W)
        lf.Label(text='• CustomTkinter (c) Tom Schimansky, MIT License'  , size=GlobalData.FONT_SMALL_SIZE, sticky=tk.W)
        lf.Label(text='• tkinter-tooltip (c) gnikit, MIT License.'       , size=GlobalData.FONT_SMALL_SIZE, sticky=tk.W)
        lf.Label(text='by Marco Servadei\n  • trallallerotrallalla@gmail.com\n  • @smarco_tg', size=GlobalData. FONT_SMALL_SIZE)

        CwcButtonTkmt(
            master          = self.window.frame(),
            image_base_name = 'close',
            command         = self.window.quit,
            row             = 1,
            col             = 0,
            padx            = 10,
            pady            = 5,
            style           = 'Toolbutton'
        )
        self.window.show()

############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    set_style()

    a = About()
    a.show()
