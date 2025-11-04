"""This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module for the handling of the buttons of the definitions.
There's a single buttons' frame for all the definitions panels.
Clicking on a definition panel enables/disables the buttons' frame.
When enabled, the panel's word is shown, when disabled, the word is hidden.
"""

import os
import inspect

import tkinter as tk

import customtkinter as ctk

from cwc_globals import (
    GlobalData,
    Direction,
    Colors,
    bind,
    get_forbid_curs
)
from word               import Word
from cwc_button         import CwcButtonCtk
from definition_element import DefinitionElement
from definition_element import ElementData, FrameState

class DefinitionButtonsFrame(ctk.CTkFrame):
    """Class for the handling of the buttons of the definitions."""

    height = 32

    def __init__(self, master:ctk.CTkFrame):
        """Creates the buttons' frame"""

        super().__init__(
            master       = master,
            width        = 1,
            height       = DefinitionButtonsFrame.height,
            fg_color     = str(Colors.grey),
            bg_color     = str(Colors.label_frame_col),
            border_width = 1,
            border_color = str(Colors.black)
        )

        self.ed:ElementData = None
        self.word:Word      = None

        bind(DefinitionElement, self.set_source, 'emit_open_definition')

        self.__current_word = ctk.CTkLabel(
            master     = self,
            text       = '',
            width      = 150,
            font       = GlobalData.TITLE_FONT,
            fg_color   = 'transparent',
            text_color = str(Colors.black),
            anchor     = tk.W
        )
        self.__current_word.grid(padx=10, pady=(2, 0), row=0, column=0, sticky=tk.EW)
        self.grid_columnconfigure(0, weight=1)

        self.__btn_reload = CwcButtonCtk(
            master          = self,
            image_base_name = 'def-reload',
            anchor          = tk.E,
            command         = lambda: DefinitionButtonsFrame.reload_definition(word=self.word)
        )

        self.__btn_reload.grid(padx=(10, 0), pady=2, row=0, column=1, sticky=tk.NSEW)
        self.grid_columnconfigure(1, weight=0)

        self.__btn_web_search = CwcButtonCtk(
            master          = self,
            image_base_name = 'def-web-search',
            anchor          = tk.E,
            command         = lambda : DefinitionButtonsFrame.web_find_definition(word=self.word)
        )
        self.__btn_web_search.grid(padx=0, pady=2, row=0, column=2, sticky=tk.NSEW)
        self.grid_columnconfigure(2, weight=0)

        self.__btn_sql_search = CwcButtonCtk(
            master          = self,
            image_base_name = 'def-sql-search',
            anchor          = tk.E,
            command         = lambda : DefinitionButtonsFrame.sql_find_definition(word=self.word)
        )
        self.__btn_sql_search.grid(padx=0, pady=2, row=0, column=3, sticky=tk.NSEW)
        self.grid_columnconfigure(3, weight=0)

        self.__btn_add_word = CwcButtonCtk(
            master          = self,
            image_base_name = 'def-add-word',
            anchor          = tk.E,
            command         = lambda : DefinitionButtonsFrame.add_word(word=self.word)
        )
        self.__btn_add_word.grid(padx=0, pady=2, row=0, column=4, sticky=tk.NSEW)
        self.grid_columnconfigure(4, weight=0)

        self.__btn_add_def = CwcButtonCtk(
            master          = self,
            image_base_name = 'def-add-def',
            anchor          = tk.E,
            command         = lambda : DefinitionButtonsFrame.add_definitions(word=self.word)
        )
        self.__btn_add_def.grid(padx=(0, 5), pady=2, row=0, column=5, sticky=tk.NSEW)
        self.grid_columnconfigure(5, weight=0)
        self.grid_rowconfigure   (0, weight=0)

        self.update_idletasks()
        self.grid_propagate(False)

    def set_source(self, ed:ElementData, *args, **kwargs):
        """Set's the caller, means the definition panel that was clicked.
        If ED is None, means the frame lost the source so it's disabled.
        The method calls a not implemented method 'emit_source_set'
        that has to be bound.
        """

        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.ed = ed
        if self.ed:
            self.word = ed.get_word()
            self.__current_word.configure(text=f'"{self.word.get_word()}"')
            self.configure(fg_color=str(Colors.very_light_blue), bg_color=str(Colors.label_frame_col))

            match self.ed.get_state():
                case FrameState.FS_EMPTY:
                    self.__btn_web_search.configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_reload    .configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_add_word  .configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_sql_search.configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_add_def   .configure(state='disabled', cursor=get_forbid_curs())
                case FrameState.FS_WORD_SET_NOT_EXISTS:
                    self.__btn_web_search.configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_reload    .configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_add_def   .configure(state='disabled', cursor=get_forbid_curs())
                    self.__btn_sql_search.configure(state='normal', cursor='hand2')
                    self.__btn_add_word  .configure(state='normal', cursor='hand2')
                case FrameState.FS_WORD_SET_EXISTS | FrameState.FS_COMPLETE:
                    self.__btn_web_search.configure(state='normal', cursor='hand2')
                    self.__btn_reload    .configure(state='normal', cursor='hand2')
                    self.__btn_sql_search.configure(state='normal', cursor='hand2')
                    self.__btn_add_def   .configure(state='normal', cursor='hand2')
                    self.__btn_add_word  .configure(state='disabled', cursor=get_forbid_curs())
            DefinitionButtonsFrame.emit_source_set(*args, **kwargs)
        else:
            self.word = None
            self.configure(fg_color=str(Colors.grey), bg_color=str(Colors.label_frame_col))
            self.__current_word.configure(text='')

            self.__btn_web_search.configure(state='disabled', cursor=get_forbid_curs())
            self.__btn_reload    .configure(state='disabled', cursor=get_forbid_curs())
            self.__btn_add_word  .configure(state='disabled', cursor=get_forbid_curs())
            self.__btn_sql_search.configure(state='disabled', cursor=get_forbid_curs())
            self.__btn_add_def   .configure(state='disabled', cursor=get_forbid_curs())

    def refresh(self):
        """Refreshes the buttons' frame according to the current source."""
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.configure(
            height   = DefinitionButtonsFrame.height,
            bg_color = str(Colors.label_frame_col)
        )

############# TESTS #############

_STATE = False

def get_state():
    globals()['_STATE'] = not globals()['_STATE']
    return globals()['_STATE']

if __name__ == "__main__":
    from cwc_style  import set_style

    set_style()

    d = DefinitionButtonsFrame(master=GlobalData.main_window)
    d.grid(padx=250, pady=10, row=0, column=0, sticky=tk.EW)

    _ed = ElementData()
    _ed.set_data(key='word', data=Word(
        coordinates = (0, 0),
        length      = 4,
        word        = 'TEST',
        direction   = Direction.HORIZONTAL
        )
    )

    bind(DefinitionButtonsFrame, lambda *args, **kwargs :
         print('emit_source_set'), 'emit_source_set')

    CwcButtonCtk(
        master  = GlobalData.main_window,
        text    = 'test',
        command = lambda : d.set_source(ed=_ed if get_state() else None),
        row     = 1,
        col     = 0,
        border_width=1,
        state   = 'normal'
    )

    GlobalData.main_window.mainloop()
