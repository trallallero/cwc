"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.

Main module for the CWC application

TODO: block archive language change if project started (has no sense)
TODO: big change->allow multiple language archives as fallback if word not found
"""


import os
import time
import tkinter as tk
from tkinter import ttk
from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals import (
    Theme,
    GlobalData,
    AppState,
    Colors,
    bind,
    clear_all,
    set_app_settings
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)

from crossword           import Crossword
from menu_frame          import MenuFrame
from cwc_templates       import CWCTemplates
from cell_handler        import CellHandler
from db_connection       import DbConnection
from definitions         import Definitions
from project             import ProjectHandler
from splash_screen       import SplashScreen
from crossword_filler    import CrosswordFiller
from dimensions          import Dimensions
from settings            import Settings
from export_launcher     import ExportLauncher
from app_thread_executor import AppThreadExecutor
from cwc_style           import set_style
from translations        import gtbk

from word import (
    set_char_to_words,
    empty_words
)

class CWC:
    """Main class for the CWC application"""

    __last_resize_value = 0

    def __init__(self) -> None:
        self.matrix_frame    :WidgetFrame = None
        self.definition_frame:WidgetFrame = None
        self.splash_screen:SplashScreen   = self.__open_splash_screen()
        self.cell_handler:CellHandler     = CellHandler()
        self.frame_upper:ttk.LabelFrame   = None
        self.frame_lower:ttk.LabelFrame   = None
        self.definitions:Definitions      = None
        self.resize_var                   = tk.DoubleVar()

        set_app_settings()
        set_style()

        self.__create_main_frames()

        MenuFrame.create(
            master    = self.frame_upper,
            widget    = self,
            variables = {
                'theme_var'      : GlobalData.THEME_VAR,
                'resize_var'     : self.resize_var,
                'appearence_var' : GlobalData.APPEARENCE_VAR
            }
        )

        self.__trace_theme_vars()

        GlobalData.main_window.geometry('1400x500+0+0')
        GlobalData.main_window.title('')
        try:
            GlobalData.main_window.iconbitmap(GlobalData.ICO_FILENAME)
        except FileNotFoundError as e:
            print(e)

        bind(Crossword, self.__finalize_crossword_caller, 'emit_finalize_crossword')
        bind(Crossword, self.__close_crossword          , 'emit_crossword_closed')

        GlobalData.main_window.after(1, GlobalData.main_window.configure(cursor=''))

    def show(self):
        if self.splash_screen:
            self.splash_screen.close()
        GlobalData.main_window.lift()
        GlobalData.main_tkmt_window.run(cleanresize=False)

    def clear_cw(self):
        """Dynamically bound from the MainButtons class"""

        GlobalData.main_window.configure(cursor='watch')
        GlobalData.main_window.update()

        with AppThreadExecutor(
            method       = self.__clear_cw_internal,
            result_state = AppState.AS_CW_FINALIZED,
            message_key  = 'clearing_cw',
            show_cancel  = False):
            pass

    def close_crossword(self):
        """Dynamically bound from the MainButtons class"""

        Crossword.close_crossword()
        CwcMatrix.clear_matrices()

    def export_cw(self):
        """Dynamically bound from the MainButtons class"""

        e = ExportLauncher()
        e.show()

    def settings(self):
        """Dynamically bound from the MainButtons class"""

        s = Settings()
        bind(s, self.__apply_theme, 'emit_style_change')
        s.show()

    def dimensions(self):
        """Dynamically bound from the MainButtons class"""

        d = Dimensions()
        bind(d, Crossword.set_font_dimension, 'set_font_dimension')
        d.show()

    def save_project(self):
        """Dynamically bound from the MainButtons class"""

        p = ProjectHandler(window=GlobalData.main_window)
        p.save()

    def open_project(self):
        """Dynamically bound from the MainButtons class"""

        clear_all() # TODO: ask user if agree
        p = ProjectHandler(window=GlobalData.main_window)
        if not p.open():
            return # TODO: handle error

        GlobalData.TOT_ROWS = len(CwcMatrix.get(matrix_type=MatrixType.BOOLEAN))
        GlobalData.TOT_COLS = len(CwcMatrix.get(matrix_type=MatrixType.BOOLEAN)[0])

        GlobalData.main_window.state(GlobalData.WINDOW_STATE)

        with AppThreadExecutor(
            method       = lambda : self.__create_crossword(is_open=True),
            message_key  = 'creating_cw',
            result_state = GlobalData.OPEN_CW_APP_STATE,
            show_cancel  = False
        ): pass

        if GlobalData.OPEN_CW_APP_STATE in [AppState.AS_CW_FINALIZED, AppState.AS_CW_FILLED, AppState.AS_CW_COMPLETE]:
            self.__finalize_crossword_caller(is_open=True)

        self.resize_var.set(GlobalData.CURRENT_SCALE_VALUE)

    def get_template(self):
        """Dynamically bound from the MainButtons class"""

        t = CWCTemplates(master=GlobalData.main_window)
        ret = t.get_template()

        if ret:
            GlobalData.TOT_ROWS          = int(ret['y'])
            GlobalData.TOT_COLS          = int(ret['x'])
            GlobalData.BLACK_PERCENT     = int(ret['black_cells'])
            GlobalData.CURRENT_FONT_SIZE = int(ret['font'])
            GlobalData.MAX_WORD_LENGTH   = int(ret['max_word_len'])

            self.__create_crossword_internal(is_open=GlobalData.BLACK_PERCENT==-1)

    def fill_crossword(self):
        """Dynamically bound from the MainButtons class"""

        with AppThreadExecutor():
            self.cell_handler.deselect_cells()

            if not CwcMatrix.get(matrix_type=MatrixType.ENTRY):
                return

            cf = CrosswordFiller(grid=self.__matrix_to_grid())
            dest_matrix = cf.run()

        self.__finished_filling(matrix=dest_matrix)

    def __create_crossword_internal(self, is_open=False):
        with AppThreadExecutor(
            method       = lambda : self.__create_crossword(is_open=is_open),
            result_state = AppState.AS_CW_CREATED,
            message_key  = 'creating_cw',
            show_cancel  = False
        ): pass

    def __trace_theme_vars(self):
        GlobalData.THEME_VAR     .set(Theme.CURRENT_APP_THEME)
        GlobalData.APPEARENCE_VAR.set(Theme.CURRENT_APP_MODE)

        GlobalData.THEME_VAR     .trace_add('write', self.__set_theme)
        GlobalData.APPEARENCE_VAR.trace_add('write', self.__set_appearence)

    def __bind_events(self):
        bind(self.cell_handler, self.definitions.highlight_definition  , 'emit_highlighted_word')
        bind(self.cell_handler, self.definitions.unhighlight_definition, 'emit_unhighlighted_word')
        bind(self.definitions , self.cell_handler.highlight_word       , 'emit_highlighted_definition')
        bind(self.definitions , self.cell_handler.unhighlight_word     , 'emit_unhighlighted_definition')

    def __open_splash_screen(self):
        ss = SplashScreen()
        time.sleep(3) # TODO, uncomment this to show the user the splash screen
        return ss

    def __resize(self, *_):
        """Bound to a Scale object, resizes the matrix and definitions frames"""

        value = int(self.resize_var.get())
        if self.definition_frame.master.winfo_width() < 100 and value > CWC.__last_resize_value:
            return
        GlobalData.CURRENT_SCALE_VALUE = value
        CWC.__last_resize_value     = value
        self.frame_lower.master.grid_columnconfigure(0, weight=max(
            GlobalData.RESIZE_MIN_VALUE, value))
        self.frame_lower.master.grid_columnconfigure(1, weight=max(
            GlobalData.RESIZE_MIN_VALUE, GlobalData.RESIZE_MAX_VALUE-value))

    def __create_main_frames(self):
        self.frame_upper = GlobalData.main_tkmt_window.addLabelFrame(
            text         = f" {gtbk('menu')} ",
            sticky       = tk.NSEW,
            padx         = 5,
            pady         = 5,
            row          = 0,
            col          = 0
        )

        self.frame_lower = GlobalData.main_tkmt_window.addFrame(
            name         = 'CWC:frame_lower',
            sticky       = tk.NSEW,
            padx         = 3,
            pady         = (0, 5),
            row          = 1,
            col          = 0,
            widgetkwargs = {'style' : 'Dynamic.TFrame'}
        )

        self.__create_matrix_frame()
        self.__create_definition_frame()

        self.definition_frame.master.grid_rowconfigure   (0, weight=1)
        self.definition_frame.master.grid_columnconfigure(0, weight=1)

        GlobalData.main_tkmt_window.root.grid_columnconfigure(0, weight=1)
        GlobalData.main_tkmt_window.root.grid_rowconfigure(0, weight=0)
        GlobalData.main_tkmt_window.root.grid_rowconfigure(1, weight=1)

        self.resize_var.trace_add('write', self.__resize)

    def __create_matrix_frame(self):
        self.matrix_frame = self.frame_lower.addLabelFrame(
            text   = f" {gtbk('matrix')} ",
            sticky = tk.NSEW,
            padx   = 2,
            pady   = (5, 0),
            row    = 0,
            col    = 0
        )
        self.frame_lower.master.grid_rowconfigure   (0, weight=1)
        self.frame_lower.master.grid_columnconfigure(0, weight=GlobalData.RESIZE_MIN_VALUE)

    def __create_definition_frame(self):
        self.definition_frame = self.frame_lower.addLabelFrame(
            text   = f" {gtbk('definitions')} ",
            sticky = tk.NSEW,
            padx   = 2,
            pady   = (5, 0),
            row    = 0,
            col    = 1
        )
        self.frame_lower.master.grid_rowconfigure   (0, weight=1)
        self.frame_lower.master.grid_columnconfigure(1, weight=GlobalData.RESIZE_MAX_VALUE)

    def __destroy_definitions(self):
        if self.definitions:
            del self.definitions
        self.definitions = None

    def __create_definitions(self):
        self.__destroy_definitions()
        self.definitions = Definitions(window=self.definition_frame.master)

    def __clear_cw_internal(self):
        """Called via the AppThreadExecutor from the method clear_cw"""

        empty_words()

        CwcMatrix.clear_matrices()

        #for y in range(GlobalData.TOT_ROWS):
        #    for x in range(GlobalData.TOT_COLS):
        #        CwcMatrix.set_variable_value(y=y, x=x, value='')

        if self.definitions:
            self.definitions.clear()

        GlobalData.main_window.update_idletasks()

    def __set_theme(self, *_):
        if GlobalData.SETTING_THEME:
            return
        theme = GlobalData.THEME_VAR.get()
        GlobalData.main_tkmt_window.set_theme(theme=theme)
        self.__set_appearence()

    def __set_appearence(self,  *_):
        theme      = GlobalData.THEME_VAR     .get()
        appearence = GlobalData.APPEARENCE_VAR.get()
        Theme.CURRENT_APP_THEME = theme
        Theme.CURRENT_APP_MODE  = appearence

        if theme == 'sun-valley':
            Colors.label_frame_col = '#1c1c1c' if appearence == 'dark' else '#fafafa'
        if theme == 'azure':
            Colors.label_frame_col = '#333333' if appearence == 'dark' else '#ffffff'
        if theme == 'park':
            Colors.label_frame_col = '#313131' if appearence == 'dark' else '#ffffff'

        GlobalData.main_window.tk.call("set_theme", GlobalData.APPEARENCE_VAR.get())
        set_style()
        Crossword.refresh()
        for c in self.frame_upper.master.children:
            if '!ctkframe' in c:
                child = self.frame_upper.master.children[c]
                child.configure(fg_color=str(Colors.label_frame_col), bg_color='transparent')
        if self.definitions:
            self.definitions.refresh()

    def __apply_theme(self, style, mode):
        GlobalData.SETTING_THEME = True
        GlobalData.THEME_VAR     .set(style)
        GlobalData.APPEARENCE_VAR.set(mode)
        GlobalData.SETTING_THEME = False

    def __create_crossword(self, is_open=False):
        Crossword.create_crossword(master=self.matrix_frame, is_open=is_open)

    def __close_crossword(self):
        GlobalData.set_current_state(AppState.AS_CW_NOT_CREATED)
        if self.definitions:
            self.definitions.destroy()
            self.definitions = None

    def __finalize_crossword_caller(self, is_open=False):
        with AppThreadExecutor(
            method       = lambda : self.__finalize_crossword(is_open=is_open),
            result_state = GlobalData.OPEN_CW_APP_STATE if is_open else AppState.AS_CW_FINALIZED,
            message_key  = 'finalizing_cw',
            show_cancel  = False
        ): pass

    def __finalize_crossword(self, is_open):
        Crossword.finalize_crossword(is_open=is_open)
        self.__create_definitions()
        self.definitions.create_definition_objects(is_open=is_open)
        self.cell_handler.bind_events()
        self.__bind_events()
        if is_open:
            GlobalData.OPEN_CW_APP_STATE = AppState.AS_CW_NOT_CREATED

    def __matrix_to_grid(self):
        grid = []
        for y, _ in enumerate(range(GlobalData.TOT_ROWS)):
            grid_row = []
            for x, _ in enumerate(range(GlobalData.TOT_COLS)):
                if not CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x):
                    grid_row.append('#')
                else:
                    grid_row.append('.')
            grid.append(''.join(grid_row))
        return grid

    def __finished_filling(self, matrix):
        with AppThreadExecutor(
            method       = lambda matrix=matrix: self.__finished_filling_internal(matrix=matrix),
            result_state = AppState.AS_NONE,
            message_key  = 'filling_words'
        ): pass

        self.__bind_events()

        GlobalData.set_current_state(AppState.AS_CW_COMPLETE if self.definitions.is_complete() else AppState.AS_CW_FILLED)

    def __finished_filling_internal(self, matrix):
        if not matrix:
            return # TODO handle this

        for y, _ in enumerate(range(len(matrix))):
            for x, _ in enumerate(range(len(matrix[0]))):
                if not AppThreadExecutor.running:
                    return
                c = matrix[y][x]
                if c != '#':
                    CwcMatrix.set_variable_value(y=y, x=x, value=c)
                    set_char_to_words(y=y, x=x, char=c)
        DbConnection().set_words_definitions()


##############################

if __name__ == "__main__":
    cwc = CWC()
    cwc.show()
