import tkinter as tk

from cwc_globals  import GlobalData
from cwc_toplevel import CwcTopLevel

class Dimensions:
    def __init__(self) -> None:
        self.window    = CwcTopLevel(title='', create_frame=False, center=False, focus=False, margin=True)
        self.font_size = tk.IntVar(value=GlobalData.CURRENT_FONT_SIZE)
        self.cb_size   = None

    def show(self):
        self.cb_size = self.window.frame().Combobox(
            values       = list(range(GlobalData.MIN_MAX_FONT_DIMENSIONS[0], GlobalData.MIN_MAX_FONT_DIMENSIONS[1] + 1)),
            variable     = self.font_size,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'postcommand' : self.dropdown_opened, 'state' : 'readonly'},
            padx         = 0,
            pady         = 0
        )
        self.font_size.set(GlobalData.CURRENT_FONT_SIZE)
        self.font_size.trace_add('write', self.__set_font_dimension)
        self.cb_size.bind("<FocusOut>", self.focus_out)
        self.cb_size.focus_set()
        self.window.show()

    def focus_out(self, *_):
        self.window.quit()

    def dropdown_opened(self):
        self.cb_size.unbind("<FocusOut>")
        self.cb_size.focus_set()
        self.window.root.after(100, lambda : self.cb_size.bind("<FocusOut>", self.window.quit))

    def __set_font_dimension(self, *_):
        GlobalData.CURRENT_FONT_SIZE = self.font_size.get()
        self.set_font_dimension()
        self.window.quit()


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    set_style()

    d = Dimensions()
    GlobalData.main_window.after(1, d.show)
    GlobalData.main_window.mainloop()
