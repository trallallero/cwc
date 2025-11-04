"""Module to define the app's style"""

import tkinter as tk
from tkinter import ttk

from cwc_globals import (
    GlobalData,
    Colors
)

def set_style():
    """Set's the style defining all the elements"""

    entry_style = ttk.Style()

    entry_style.configure(
        'Red.TFrame',
        borderwidth = 1,
        background  = Colors.light_red
    )
    entry_style.configure(
        'Red.Label',
        borderwidth = 0,
        background  = Colors.red
    )
    entry_style.configure(
        'White.Label',
        borderwidth = 0,
        background  = Colors.white,
        foreground  = Colors.black
    )
    entry_style.configure(
        'Black.Label',
        borderwidth = 0,
        background  = Colors.black,
        state       = 'disabled'
    )
    entry_style.configure(
        'Highlight.Label',
        borderwidth = 0,
        background  = Colors.yellow,
        foreground  = Colors.blue
    )
    entry_style.configure(
        'Orange.Label',
        borderwidth = 0,
        background  = Colors.orange,
        foreground  = Colors.black
    )
    entry_style.configure(
        'TFrame',
        borderwidth = 1,
        background  = Colors.light_grey
    )
    entry_style.configure(
        'White.TFrame',
        borderwidth = 0,
        background  = Colors.white
    )
    entry_style.configure(
        'Black.TFrame',
        borderwidth = 0,
        background  = Colors.black
    )
    entry_style.configure(
        'Grey.TFrame',
        borderwidth = 0,
        background  = Colors.grey
    )
    entry_style.configure(
        "Custom.TFrame",
        borderwidth = 3,
        background  = Colors.cwc_button_border
    )
    entry_style.configure(
        'Volatile.TLabel',
        borderwidth = 1,
        background  = Colors.grey,
        foreground  = Colors.black
    )
    entry_style.configure(
        'CwcTopLevel.TFrame',
        borderwidth = 0,
        relief      = tk.FLAT,
        background  = Colors.cwc_toplevel
    )
    entry_style.configure(
        'TCheckbutton',
        font = ('Helvetica', 8)
    )
    entry_style.configure('Custom.TCombobox',
        font         = GlobalData.SMALL_COMBO_FONT,
        padding      = 0,
        border_width = 1
    )
    entry_style.configure(
        'Transp.TFrame',
        borderwidth = 0,
        background  = '',
        relief      = tk.FLAT
    )
    entry_style.configure(
        'TButton',
        borderwidth = 1,
        focuscolor  = Colors.blue,
        font        = GlobalData.MAIN_BUTTON_FONT
    )

    # dynamically gets the color of the LabelFrame to allow the creation of
    # "transparent" frames -> 'Dynamic.TFrame'
    if not Colors.label_frame_col:
        Colors.label_frame_col = entry_style.lookup('TLabelframe', 'background')

    entry_style.configure(
        'Dynamic.TFrame',
        borderwidth = 0,
        background  = Colors.label_frame_col,
        relief      = tk.FLAT
    )

############# TESTS #############

if __name__ == "__main__":
    set_style() # does nothing, just make sure there's no error
