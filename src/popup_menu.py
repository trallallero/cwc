"""Module for the crossword popup menu"""

import tkinter as tk
from tkinter import ttk

from cwc_toplevel_tk import CwcTopLevel

from cwc_globals import (
    GlobalData,
    Colors,
    bind
)
from translations import (
    gtbk,
    gkbv
)
from cell_entry import CellEntry

MARGIN = GlobalData.POPUP_MENU_WINDOW_MARGIN # shorter

# Defines the methods of the menu for a cell with a word
# 'sep' means separator
words_labels = [
    'find_word',
    'sep',
    'del_word',
    'del_find_word',
    'del_exclude_word_once',
    'del_exclude_word_session',
    'del_exclude_word_always',
    'sep',
    'del_other_words',
    'sep',
    'del_not_used_keys',
    'del_find_not_used_keys',
    'sep',
    'del_char',
    'sep',
    'handle_word'
]

# Defines the methods of the menu for a cell without a word
no_words_labels = [
    'del_char'
]

class PopupMenu(CwcTopLevel):
    """Class for the crossword popup menu"""

    def __init__(self, master:CellEntry, text_func_map=None, **kwargs):
        super().__init__(**kwargs)

        self.master = master
        self.attributes('-topmost', True)

        # Defines the enabled condition for each menu item
        self.text_func_map = {
            'find_word'                : True                      ,
            'del_word'                 : not self.master.is_empty(),
            'del_find_word'            : not self.master.is_empty(),
            'del_exclude_word_once'    : not self.master.is_empty(),
            'del_exclude_word_session' : not self.master.is_empty(),
            'del_exclude_word_always'  : False, # TODO
            'del_other_words'          : not self.master.is_empty(),
            'del_not_used_keys'        : not self.master.is_empty(),
            'del_find_not_used_keys'   : not self.master.is_empty(),
            'del_char'                 :     self.master.get() != '',
            'handle_word'              : not self.master.is_empty()
        } if text_func_map is None else text_func_map

        self.__create_menu_commands(user_defined=text_func_map is not None)

    def __create_menu_commands(self, user_defined):
        transp_frame = tk.Frame(master=self, relief=tk.FLAT, borderwidth=0, background='')
        transp_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        menu_frame = ttk.Frame(master=transp_frame, relief=tk.SOLID, borderwidth=2, style='TFrame', takefocus=1)
        menu_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, ipadx=10, padx=MARGIN, pady=MARGIN)

        transp_frame.bind("<Leave>"   , self.quit)
        transp_frame.bind("<Button-1>", self.quit)
        transp_frame.bind("<FocusOut>", self.quit) # need to quit if somehow the TopLevel lost focus or main window freezes

        labels = words_labels                                      \
            if (not user_defined and len(self.master.words())) > 0 \
            else no_words_labels                                   \
                if not user_defined                                \
                else self.__get_labels_from_text_func_map()
        for key in labels:
            if key == 'sep':
                ttk.Separator(master=menu_frame, orient='horizontal').pack(side=tk.TOP, fill=tk.X, expand=True, pady=2, padx=10)
            else:
                self.__create_label(frame=menu_frame, key=key)
        self.__bind_labels(parent=menu_frame)

    def __get_labels_from_text_func_map(self):
        keys = []
        for key, value in self.text_func_map.items():
            keys.append(key)
        return keys

    def __create_label(self, frame, key):
        state = 'normal' if self.text_func_map[key] else 'disabled'
        text  = gtbk(key=key)
        ttk.Label(
            master     = frame,
            text       = text,
            anchor     = tk.W,
            justify    = tk.LEFT,
            padding    = 3,
            state      = state,
            background = Colors.light_grey,
            font       = (GlobalData.CURRENT_FONT_NAME, 8) if state == 'normal' else (GlobalData.CURRENT_FONT_NAME, 8, 'italic')
        ).pack(side=tk.TOP, fill=tk.X, expand=True, pady=3, padx=3)

    def __bind_labels(self, parent):
        for child in parent.winfo_children():
            if child.widgetName == 'ttk::label':
                text   = child.cget('text')
                method = gkbv(value=text)
                child.bind('<Enter>'   , self.__highlight_label)
                child.bind('<Leave>'   , self.__unhighlight_label)
                child.bind('<Button-1>', lambda x, key=method : self.__execute_method(key, widget=self.master))
                self.__unhighlight_label(widget=child)

    def __execute_method(self, key, widget):
        self.after(1, self.quit)                  # close the popup menu after a short delay
        self.menu_method(key=key, widget=widget)  # Signal bound to a method in owner

    def __highlight_label(self, event):
        if str(event.widget['state']) == 'normal':
            event.widget.configure(background=Colors.light_yellow, foreground=Colors.black, cursor='hand2')

    def __unhighlight_label(self, event=None, widget=None):
        lbl = event.widget if event else widget
        if str(lbl['state']) == 'normal':
            lbl.configure(background=Colors.light_grey, foreground=Colors.dark_grey)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style
    import customtkinter as ctk

    set_style()

    tl = GlobalData.main_window
    f = ttk.Frame(master=tl)
    f.grid(row=0, column=0)

    _frame = ctk.CTkScrollableFrame(
        master                       = f,
        orientation                  = 'horizontal',
        fg_color                     = 'transparent',
        border_color                 = Colors.light_grey,
        scrollbar_button_hover_color = Colors.orange,
        height                       = 60,
        border_width                 = 0
    )
    _frame.grid(padx=3, pady=3, row=0, column=0, sticky=tk.EW)
    p = PopupMenu(master=_frame, text_func_map={'delete' : True})
    bind(p, lambda *args, **kargs: print('menu_method'), 'menu_method')
    p.show()

    c = CellEntry(master=f, y=0, x=0, textvariable=None)
    p = PopupMenu(master=c, text_func_map={'delete' : True})
    p.show()

    p = PopupMenu(master=c)
    p.show()

    # test menu without a word
    c.clear()
    p = PopupMenu(master=c)
    p.show()
