"""
This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to handle crossword's definitions

TODO: document it
"""

import os
import inspect
import webbrowser

import tkinter as tk

import pyautogui

import customtkinter as ctk

from cwc_globals import (
    Theme,
    AppState,
    GlobalData,
    Direction,
    Colors,
    bind,
    unbind,
    get_search_defs_url,
    get_parent_widget
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)

from db_connection            import DbConnection
from translations             import gtbk
from definition_element       import DefinitionElement
from input_panel              import InputPanel
from app_thread_executor      import AppThreadExecutor
from definition_buttons_frame import DefinitionButtonsFrame
from sql_search_frame         import SqlSearchFrame
from word_editor              import WordEditor

class Definitions:
    def __init__(self, window:tk.Frame):
        """Class to handle crossword's definitions.
        TODO: document it
        """

        self.window     :tk.Frame               = window
        self.label_frame:ctk.CTkFrame           = None
        self.frame_left :ctk.CTkScrollableFrame = None
        self.frame_right:ctk.CTkScrollableFrame = None
        self.inner_frame:ctk.CTkFrame           = None
        self.dbf        :DefinitionButtonsFrame = None

        bind(DefinitionButtonsFrame, self.__reload_definition    , 'reload_definition'            )
        bind(DefinitionButtonsFrame, self.__web_find_definition  , 'web_find_definition'          )
        bind(DefinitionButtonsFrame, self.__sql_find_definition  , 'sql_find_definition'          )
        bind(DefinitionButtonsFrame, self.__add_word             , 'add_word'                     )
        bind(DefinitionButtonsFrame, self.__add_definitions      , 'add_definitions'              )
        bind(DefinitionButtonsFrame, self.__move_to_definition   , 'emit_source_set'              )
        bind(DefinitionElement     , self.__add_definitions      , 'add_definitions'              )
        bind(DefinitionElement     , self.__full_word_set        , 'emit_full_word_set'           )
        bind(DefinitionElement     , self.highlight_definition   , 'emit_highlighted_definition'  )
        bind(DefinitionElement     , self.unhighlight_definition , 'emit_unhighlighted_definition')
        bind(WordEditor            , self.__reload_definition    , 'emit_definition_changed'      )
        bind(AppThreadExecutor     , DefinitionElement.set_busy  , 'emit_started'                 )
        bind(AppThreadExecutor     , DefinitionElement.set_unbusy, 'emit_finished'                )

        bind(
            DefinitionElement,
            lambda *args, **kargs : self.dbf.set_source(ed=None),
            'emit_definition_closed'
        )

    def destroy(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        unbind(AppThreadExecutor, 'emit_started' )
        unbind(AppThreadExecutor, 'emit_finished')

        DefinitionElement.destroy()

        if self.label_frame:
            self.label_frame.destroy()
        if self.frame_left :
            self.frame_left .destroy()
        if self.frame_right:
            self.frame_right.destroy()
        if self.inner_frame:
            self.inner_frame.destroy()
        if self.dbf:
            self.dbf.destroy()

        self.label_frame = None
        self.frame_left  = None
        self.frame_right = None
        self.inner_frame = None
        self.dbf         = None

    def clear(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        DefinitionElement.clear()

    def create_definition_objects(self, is_open):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        try:
            self.__create()

            for word in GlobalData.words:
                with DefinitionElement(
                    masters = (self.frame_left, self.frame_right),
                    word    = word,
                    is_open = is_open
                ): pass

            DefinitionElement.bind_external_elements()

            self.__grid_frames()
            self.__update_size()

        except Exception as e:
            print(e)

    def refresh(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if self.inner_frame:
            self.inner_frame.configure(fg_color=str(Colors.label_frame_col), bg_color='transparent')

        if self.frame_left:
            self.frame_left.configure(
                fg_color               = str(Colors.label_frame_col),
                bg_color               ='transparent',
                scrollbar_button_color = Colors.very_light_grey if Theme.CURRENT_APP_MODE == 'light' else Colors.grey
            )
        if self.frame_right:
            self.frame_right.configure(
                fg_color               = str(Colors.label_frame_col),
                bg_color               ='transparent',
                scrollbar_button_color = Colors.very_light_grey if Theme.CURRENT_APP_MODE == 'light' else Colors.grey
            )

        if self.label_frame:
            self.label_frame.configure(fg_color=str(Colors.label_frame_col), bg_color='transparent')
            for c in self.label_frame.children.items():
                if '!ctklabel' in c[0]:
                    c[1].configure(fg_color=str(Colors.label_frame_col), bg_color='transparent')

    def highlight_definition(self, word):
        #print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.emit_highlighted_definition(word=word)

    def unhighlight_definition(self, word):
        #print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.emit_unhighlighted_definition(word=word)

    def is_complete(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        return DefinitionElement.is_complete()

    def __grid_frames(self):
        self.frame_left .grid(padx=5, pady=0, row=0, column=0, sticky=tk.NSEW)
        self.frame_right.grid(padx=5, pady=0, row=0, column=1, sticky=tk.NSEW)

    def __full_word_set(self, word):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.__reload_definition(word=word)

        self.refresh()
        DefinitionElement.refresh()

    def __create(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        try:
            DefinitionElement.clear()

            self.__create_buttons_frame    ()
            self.__create_labels_frame     ()
            self.__create_inner_frame      ()
            self.__create_scrollable_frames()

            self.refresh()
        except Exception as e:
            print(e)

    def __create_buttons_frame(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.dbf = DefinitionButtonsFrame(master=self.window)
        bind(DefinitionElement, lambda *args, **kwargs: self.dbf.set_source(ed=None), 'emit_word_complete')
        self.dbf.grid(padx=250, pady=3, row=0, column=0, sticky=tk.EW)

    def __create_labels_frame(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if self.label_frame:
            self.label_frame.destroy()

        self.label_frame = ctk.CTkFrame(master=self.window, height=1, border_width=0)

        ctk.CTkLabel(
            master        = self.label_frame,
            text          = gtbk('horizontal'),
            width         = 100,
            corner_radius = 4,
            text_color    = Colors.orange,
            font          = GlobalData.TITLE_FONT
        ).grid(padx=10, pady=0, row=0, column=0, sticky=tk.EW)

        ctk.CTkLabel(
            master        = self.label_frame,
            text          = gtbk('vertical'),
            width         = 100,
            corner_radius = 4,
            text_color    = Colors.orange,
            font          = GlobalData.TITLE_FONT
        ).grid(padx=10, pady=0, row=0, column=1, sticky=tk.EW)

        self.label_frame.grid_rowconfigure   (0, weight=0)
        self.label_frame.grid_columnconfigure(0, weight=1)
        self.label_frame.grid_columnconfigure(1, weight=1)

    def __create_inner_frame(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if self.inner_frame:
            self.inner_frame.master.destroy()

        self.inner_frame = ctk.CTkFrame(master=self.window, border_width=0)

    def __inner_frame_configure(self, *_):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.__update_size()

    def __create_scrollable_frames(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.frame_left = ctk.CTkScrollableFrame(
            master                       = self.inner_frame,
            orientation                  = 'both',
            border_color                 = Colors.light_grey,
            scrollbar_button_hover_color = Colors.orange,
            border_width                 = 1
        ) # will be grid later

        self.frame_right = ctk.CTkScrollableFrame(
            master                       = self.inner_frame,
            orientation                  = 'both',
            border_color                 = Colors.light_grey,
            scrollbar_button_hover_color = Colors.orange,
            border_width                 = 1
        ) # will be grid later

        self.inner_frame.grid_rowconfigure   (0, weight=1)
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)

        self.frame_left .grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)

        pw = get_parent_widget(widget=self.frame_left)
        pw.update()
        DefinitionElement.definition_frame_width = pw.winfo_width() - 20
        pw.bind('<Configure>', self.__inner_frame_configure)

    def __update_size(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if not self.inner_frame or not self.label_frame:
            return

        if self.inner_frame.winfo_manager():
            self.inner_frame.grid_forget()

        if self.label_frame.winfo_manager():
            self.label_frame.grid_forget()

        DefinitionElement.update_size()

        self.label_frame.grid(padx=10, pady=0     , row=1, column=0, sticky=(tk.N, tk.E, tk.W))
        self.inner_frame.grid(padx=5 , pady=(0,10), row=2, column=0, sticky=tk.NSEW)

        self.window.grid_rowconfigure   (0, weight=0)
        self.window.grid_rowconfigure   (1, weight=0)
        self.window.grid_rowconfigure   (2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.dbf.refresh

    def __move_to_definition(self, parent_frame, frame:ctk.CTkFrame, *args, **kargs):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        del args
        canvas = parent_frame.canvas()
        canvas.update_idletasks()
        children = [c[1] for c in canvas.children['!ctkscrollableframe'].children.items()]
        packed_count = sum(1 for frm in children if frm.winfo_manager())

        v = None
        for i, frm in enumerate([frm for frm in children if frm.winfo_manager()]):
            if frm == frame:
                # find the nearest position (v) using number of items (packed_count) and item index (i)
                v = (0 if i <= 1 else 1 if i >= packed_count - 1 else round((i+1) / packed_count, 2))
                canvas.yview_moveto(v)
                # get the position of the container frame using item index and the height of the item + pady
                canvas.update()
                position = -((i) * (DefinitionElement.main_frame_height + DefinitionElement.main_frame_pady))
                # now scroll untill the frame is visible
                while v > 0.0 and v < 1.0 and parent_frame.winfo_y() < position:
                    v -= 0.1
                    canvas.yview_moveto(v)
                    canvas.update()
                # if sender is None means it is called from click on defintion frame
                # if sender is not None means it is called from click on cell in matrix
                if 'sender' in kargs and not kargs['sender']:
                    pyautogui.moveTo(pyautogui.position()[0], frame.winfo_rooty() + 20)
                break

    def __add_definitions(self, word):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        definitions = InputPanel(title=f'{gtbk("add_def_for")}"{word.get_word()}"', current_value='').get_values()
        if len(definitions) == 0:
            return

        if not DbConnection().add_definitions(word=word, definitions=definitions):
            return # TODO: handle this error

        DefinitionElement.add_definitions_to_listbox(word=word, definitions=definitions)

    def __web_find_definition(self, word=None):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if word:
            url = get_search_defs_url()
            if url:
                url = url.format(word=word.get_word())
                webbrowser.open(url)

    def __sql_find_definition(self, word=None):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        SqlSearchFrame(word=word).show()

    def __add_word(self, word=None):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if word:
            if DbConnection().add_word(word=word.get_word()):
                self.__reload_definition(word=word)

    def __reload_definition(self, word=None):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if not word:
            return

        word.clear_definitions()
        definitions = None
        word_exists = False if word.is_empty() else DbConnection().word_exists(word=word.get_word())
        if word_exists:
            definitions = DbConnection().get_definitions(word=word.get_word())
            if len(definitions) > 0:
                DefinitionElement.add_definitions_to_listbox(word=word, definitions=definitions, clear=True)
                for _d in definitions:
                    word.add_definition(definition=_d)
        if not definitions:
            DefinitionElement.update_frame_without_definitions(word=word, word_exists=word_exists)
        if self.is_complete():
            self.dbf.set_source(ed=None)
            GlobalData.set_current_state(AppState.AS_CW_COMPLETE)


############# TESTS #############

if __name__ == "__main__":
    from word import Word
    from cwc_style import set_style

    set_style()

    GlobalData.main_window.geometry('1000x400')
    GlobalData.main_window.update_idletasks()
    for ii in range(3):
        GlobalData.words.append(Word(
                coordinates = (ii, 0),
                length      = 6,
                word        = 'TEST' if ii == 0 else 'PROVA',
                direction   = Direction.HORIZONTAL
            ))
        CwcMatrix.set(matrix_type=MatrixType.VARIABLE, y=ii, x=0, value=tk.StringVar())
        CwcMatrix.set(matrix_type=MatrixType.NUMBER  , y=ii, x=0, value=tk.Label())

        GlobalData.words.append(Word(
                coordinates = (0, ii),
                length      = 5,
                word        = 'CASA' if ii == 0 else 'ALBERO',
                direction   = Direction.VERTICAL
            ))
        CwcMatrix.set(matrix_type=MatrixType.VARIABLE, y=0, x=ii, value=tk.StringVar())
        CwcMatrix.set(matrix_type=MatrixType.NUMBER  , y=0, x=ii, value=tk.Label())

    f = GlobalData.main_tkmt_window.addLabelFrame(' Definizioni ', sticky=tk.NSEW, padx=5, pady=5, row=0, col=0)
    GlobalData.main_tkmt_window.root.grid_rowconfigure   (0, weight=1)
    GlobalData.main_tkmt_window.root.grid_columnconfigure(0, weight=1)

    d = Definitions(window=f.master)
    bind(d, lambda *args, **kargs : None, 'emit_highlighted_definition')
    bind(d, lambda *args, **kargs : None, 'emit_unhighlighted_definition')
    d.create_definition_objects(is_open=False)
    GlobalData.CH_HIDE_VAR.set(False)
    GlobalData.main_window.after(500, lambda : Word.emit_full_word_set(word=GlobalData.words[0]))
    GlobalData.main_tkmt_window.root.mainloop()
