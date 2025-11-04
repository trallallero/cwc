""" Module defining the CellEntry - means white cell - class for crossword grid cells. """

from tkinter import ttk

from cwc_globals import (
    GlobalData,
    Direction,
    get_matrix_dimensions
)
from cell_base import CellBase

class CellEntry(ttk.Entry, CellBase):
    """ Class defining the CellEntry - means white cell - class for crossword grid cells. """

    def __init__(self, master, y, x, **kwargs):
        super().__init__(
            master  = master,
            font    = (GlobalData.CURRENT_FONT_NAME, get_matrix_dimensions('white_font'), 'bold'),
            width   = 3,
            justify = 'center',
            state   = 'disabled',
            **kwargs
        )

        CellBase.__init__(self, y=y, x=x, widget=self)

    def get_direction(self):
        if len(self.words()) == 1:
            return self.words()[0].get_direction()
        return Direction.NONE

    def get_text(self):
        return self.get()

############# TESTS #############

if __name__ == "__main__":
    from word import Word

    ce = CellEntry(master=GlobalData.main_window, y=0, x=0)

    assert ce.get_direction() == Direction.NONE

    ce.add_word(w=Word(
            coordinates = (0, 0),
            length      = 4,
            word        = 'TEST',
            direction   = Direction.VERTICAL
        )
    )
    assert ce.get_direction  ()   == Direction.VERTICAL
    assert ce.get_highlighter()   is None
    ce.set_highlighter()
    assert ce.get_highlighter()   is not None
    assert ce.get_word(text=True) == 'TEST'
