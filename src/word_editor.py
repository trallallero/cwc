"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to handle the crossword word editor.
The WordEditor allows to add/remove a word to the DB, add/remove/modify
the word's definitions.
"""

import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk

from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals import (
    Direction,
    Colors
)
from db_connection import DbConnection
from cwc_button    import CwcButtonTkmt
from input_panel   import InputPanel
from cwc_toplevel  import CwcTopLevel
from translations  import gtbk

class WordEditor:
    """Class to handle the crossword word editor."""

    def __init__(self, word, center_to_screen=False) -> None:
        self.word               = word
        self.window             = CwcTopLevel(title='word editor')
        self.btn_add_wrd        = None
        self.btn_del_wrd        = None
        self.btn_add_def        = None
        self.btn_del_def        = None
        self.btn_mod_def        = None
        self.listbox            = None
        self.current_definition = ''
        self.word_exists        = self.__word_exists()

        self.__create()
        self.window.root.lift() # for some reason, this is needed to show the window
        self.window.show(center_to_screen=center_to_screen)

    def __create(self):
        self.__create_label_frame      (master=self.window.frame())
        self.__create_word_frame       (master=self.window.frame())
        self.__create_definitions_frame(master=self.window.frame())
        self.__create_buttons_frame    (master=self.window.frame())
        self.__enable_words_buttons    ()
        self.__enable_defs_buttons     ()

    def __create_label_frame(self, master:WidgetFrame):
        master.Label(
            text         = gtbk('word_handle') + f'    "{self.word.get_word()}"',
            size         = 10,
            padx         = 10,
            pady         = 5,
            row          = 0,
            col          = 0,
            colspan      = 3,
            sticky       = tk.NSEW,
            widgetkwargs = {'anchor' : tk.CENTER}
        )

    def __create_word_frame(self, master:WidgetFrame):
        master.Seperator(padx=10, pady=3, row=1, col=0, colspan=3)

        frame_btn = WidgetFrame(master=master, name='WordEditor:word_buttons')

        master.Label(
            text         = gtbk('archive'),
            size         = 10,
            padx         = 10,
            pady         = 5,
            row          = 2,
            col          = 0,
            colspan      = 3,
            sticky       = tk.NSEW,
            widgetkwargs = {'anchor' : tk.CENTER}
        )

        self.btn_add_wrd = CwcButtonTkmt(
            master          = frame_btn.master,
            image_base_name = 'add',
            command         = self.__add_word_to_db,
            size            = 24,
            padx            = 10,
            pady            = 0,
            row             = 3,
            col             = 0,
            style           = 'Toolbutton'
        )
        self.btn_del_wrd = CwcButtonTkmt(
            master          = frame_btn.master,
            image_base_name = 'remove',
            command         = self.__remove_word_from_db,
            size            = 24,
            padx            = 10,
            pady            = 0,
            row             = 3,
            col             = 2,
            style           = 'Toolbutton'
        )

    def __create_definitions_frame(self, master:WidgetFrame):
        master.Seperator(padx=10, pady=3, row=4, col=0, colspan=3)

        master.Label(text=gtbk('definitions'), size=10, padx=0, pady=5, row=5, col=0, colspan=3)

        definitions = DbConnection().get_definitions(word=f"{self.word.get_word()}")
        max_length  = self.__get_max_definition_length(definitions=definitions)

        self.listbox = tk.Listbox(master=master.master, height=len(definitions), relief=tk.FLAT, background=Colors.very_light_grey)
        self.listbox.bind('<ButtonRelease-1>', self.__definition_selected)
        self.listbox.grid(row=6, column=0, columnspan=3, padx=(10,0), sticky=tk.NSEW)

        scrollbar = ttk.Scrollbar(master=master.master, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.config(command=self.listbox.yview, cursor='hand2')
        scrollbar.grid(row=6, column=3, sticky=tk.NSEW, padx=(0, 10), pady=5)

        self.listbox.configure(yscrollcommand=scrollbar.set, width=max_length, height=min(10, len(definitions)), foreground=Colors.black)

        for d in definitions:
            self.listbox.insert(tk.END, d)

        menu_frame_btns = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        menu_frame_btns.grid(row=7, column=0, columnspan=3)
        frame_btn = WidgetFrame(master=menu_frame_btns, name='WordEditor:frame_buttons')

        self.btn_add_def = CwcButtonTkmt(
            master          = frame_btn,
            image_base_name = 'add',
            command         = self.__add_definition_to_db,
            size            = 24,
            padx            = 2,
            pady            = 5,
            row             = 8,
            col             = 0,
            style           = 'Toolbutton'
        )
        self.btn_del_def = CwcButtonTkmt(
            master          = frame_btn,
            image_base_name = 'remove',
            command         = self.__remove_definition_from_db,
            size            = 24,
            padx            = 2,
            pady            = 5,
            row             = 8,
            col             = 1,
            style           = 'Toolbutton'
        )
        self.btn_mod_def = CwcButtonTkmt(
            master          = frame_btn,
            text            = '',
            image_base_name = 'edit',
            command         = self.__modify_definition_to_db,
            size            = 24,
            padx            = 2,
            pady            = 5,
            row             = 8,
            col             = 2,
            style           = 'Toolbutton'
        )

    def __create_buttons_frame(self, master:WidgetFrame):
        master.Seperator(padx=10, pady=3, row=9, col=0, colspan=3)

        menu_frame_btns = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        menu_frame_btns.grid(row=10, column=0, columnspan=3)

        frame_btn = WidgetFrame(master=menu_frame_btns, name='WordEditor:close_frame_button')

        CwcButtonTkmt(
            master          = frame_btn,
            image_base_name = 'close',
            command         = self.window.quit,
            padx            = 30,
            pady            = (1, 3),
            row             = 0,
            col             = 0,
            size            = 24,
            style           = 'Toolbutton'
        )

    def __enable_defs_buttons(self, definition=''):
        state = 'disabled' if definition == '' else 'normal'
        self.btn_del_def.configure(state=state)
        self.btn_mod_def.configure(state=state)
        self.btn_add_def.configure(state='normal' if self.word_exists else 'disabled')

    def __enable_words_buttons(self, *_):
        self.btn_del_wrd.configure(state='normal'   if self.word_exists else 'disabled')
        self.btn_add_wrd.configure(state='disabled' if self.word_exists else 'normal')

    def __get_max_definition_length(self, definitions):
        max_length = 60
        for d in definitions:
            max_length = max(max_length, len(d[1]))
        return max_length

    def __definition_selected(self, *_):
        # have to do it in this way because if you click and release the mouse in another position, the selection is not updated
        selected_indices = self.listbox.curselection()
        if selected_indices:
            selected_index          = selected_indices
            self.current_definition = self.listbox.get(selected_index)
            if self.current_definition == '':
                self.listbox.selection_clear(0, tk.END)
            self.__enable_defs_buttons(definition=self.current_definition)

    def __add_word_to_db(self):
        if DbConnection().add_word(word=self.word.get_word()):
            self.word_exists = True
            self.__enable_words_buttons()
            self.__enable_defs_buttons()
        else:
            pass # TODO: handle error

    def __remove_word_from_db(self):
        if DbConnection().remove_word(word=self.word.get_word()):
            self.listbox.delete(0, tk.END)
            self.listbox.configure(height=1)
            self.word_exists = False
            self.__enable_defs_buttons()
            self.__enable_words_buttons()
            self.current_definition = ''
        else:
            pass # TODO: handle error

    def __remove_definition_from_db(self):
        if DbConnection().remove_definition(definition=self.current_definition.replace("'", "''")):
            self.listbox.delete(tk.ACTIVE)
            self.listbox.configure(height=self.listbox.size())
            self.current_definition = ''
            if self.listbox.size() <= 0:
                self.listbox.grid_forget()
            self.__enable_defs_buttons()
            self.__emit_definition_changed()
        else:
            pass # TODO: handle error

    def __add_definition_to_db(self):
        new_definition = InputPanel(title=gtbk('definition')).get_value()
        if new_definition == '':
            return
        if DbConnection().add_definitions(word=self.word.get_word(), definitions=[new_definition]):
            self.listbox.insert(tk.END, new_definition)
            self.listbox.grid(row=6, column=0, columnspan=3, padx=(10,0), sticky=tk.NSEW)
            self.listbox.configure(height=self.listbox.size())
            self.current_definition = ''
            self.__enable_defs_buttons()
            self.__emit_definition_changed()
        else:
            pass # TODO: handle error

    def __modify_definition_to_db(self):
        new_definition = InputPanel(title=f'{gtbk("edit")}: "{self.current_definition}"', current_value=self.current_definition).get_value()
        if new_definition == '':
            return
        if DbConnection().update_definition(old_definition=self.current_definition, new_definition=new_definition):
            self.listbox.delete(tk.ACTIVE)
            self.listbox.insert(tk.END, new_definition)
            self.listbox.configure(height=self.listbox.size())
            self.current_definition = ''
            self.__enable_defs_buttons()
            self.__emit_definition_changed()
        else:
            pass # TODO: handle error

    def __word_exists(self):
        return len(DbConnection().get_words_by_like(like=self.word.get_word())) > 0

    def __emit_definition_changed(self):
        if hasattr(WordEditor, 'emit_definition_changed') and \
            callable(getattr(WordEditor, 'emit_definition_changed')):
            WordEditor.emit_definition_changed(word=self.word)

############# TESTS #############

if __name__ == "__main__":
    from word import Word
    from cwc_style import set_style

    set_style()

    wh = WordEditor(
        center_to_screen = True,
        word             = Word(
            coordinates = (0, 0),
            length      = 4,
            word        = 'TEST',
            direction   = Direction.HORIZONTAL
        )
    )
