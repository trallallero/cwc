""" Module defining the CellLabel - means the number of the white cell -
class for crossword grid cells.
"""

from tkinter import ttk

from cell_base   import CellBase
from cwc_globals import (
    GlobalData,
    Direction,
    Colors,
    get_matrix_dimensions
)

class CellLabel(ttk.Label, CellBase):
    """ Class defining the CellLabel - means the number of the white cell -
    class for crossword grid cells.
    """

    def __init__(self, master, y, x, **kwargs):
        super().__init__(master, font=(GlobalData.CURRENT_FONT_NAME, get_matrix_dimensions('number_font')), **kwargs)
        CellBase.__init__(self, y=y, x=x, widget=self)

    def clear(self):
        self.configure(text='')
        super().clear()

    def highlight(self):
        self.configure(foreground=Colors.blue, background=Colors.yellow)

    def unhighlight(self):
        self.configure(foreground=Colors.black, background=Colors.white)

    def select(self):
        self.configure(foreground=Colors.blue, background=Colors.orange)

    def set_text(self, text):
        self.configure(text=text)

############# TESTS #############

if __name__ == "__main__":
    assert CellLabel(master=GlobalData.main_window, y=0, x=0).get_direction() == Direction.NONE
    assert CellLabel(master=GlobalData.main_window, y=0, x=0).get_text     () == ''
