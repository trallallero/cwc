"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to handle applications's settings."""

import os
import inspect
import csv
import tkinter as tk

import customtkinter as ctk

from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals import (
    Theme,
    GlobalData,
    Colors,
    get_settings,
    save_settings,
    get_black_cells_type,
    change_language,
    get_language_code,
    bind
)

from cwc_button       import CwcButtonTkmt
from cwc_templates    import CWCTemplates
from volatile_message import VolatileMessage
from cwc_toplevel     import CwcTopLevel
from input_panel      import InputPanel
from menu_frame       import MenuFrame
from translations     import gtbk


class Settings:
    """Class to handle applications's settings.
    It calls MenuFrame for the creation of some panel.
    It calls a not implemented method 'emit_style_change' that has to be bound.
    """

    def __init__(self) -> None:
        self.window                       = CwcTopLevel(title=gtbk('settings'), center=False)
        self.online_defs_search_add_words = tk.StringVar()
        self.theme_var                    = tk.StringVar()
        self.mode_var                     = tk.StringVar()
        self.language_var                 = tk.StringVar()
        self.arch_language_var            = tk.StringVar()
        self.cwc_templ                    = CWCTemplates()
        self.online_search_engine         = ''

        self.__create()

    def show(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.window.show(center_to_screen=False)

    def __create(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.settings = get_settings()

        self.__create_cw_frame         (main_frame=self.window.frame())
        self.__create_definitions_frame(main_frame=self.window.frame())
        self.__create_editing_frame    (main_frame=self.window.frame())
        self.__create_appearance_frame (main_frame=self.window.frame())
        self.__create_buttons_frame    (main_frame=self.window.frame())

        self.language_var.trace_add('write', lambda event, *_ : change_language(get_language_code(language=self.language_var.get())))

    def __create_cw_frame(self, main_frame:WidgetFrame):
        main_frame.Label(text=gtbk('cw'), size=10, padx=2, pady=(10, 15), row=0, col=0, colspan=2)

        self.cwc_templ.create(master=main_frame, row=1)

    def __create_definitions_frame(self, main_frame:WidgetFrame):
        main_frame.Seperator(padx=10, pady=(10, 5), row=4, col=0, colspan=2)

        main_frame.Label(text=gtbk('definitions'), size=10, row=5, col=0, colspan=2)

        MenuFrame.create_definitions_frame(master=main_frame, frame_col=0, frame_row=6, create_title=False)

        engine_frame = main_frame.addFrame(
            name         = 'Settings:engine_frame',
            widgetkwargs = {'style' : 'Dynamic.TFrame'},
            row          = 8,
            col          = 0,
            colspan      = 2,
            padx         = 0,
            pady         = 0
        )
        frm1 = engine_frame.addFrame(
            name         = 'Settings:frm1',
            use_tk       = True,
            widgetkwargs = {'relief' : tk.FLAT, 'borderwidth' : 0, 'background' : Colors.label_frame_col },
            row          = 0,
            col          = 0,
            padx         = 0,
            pady         = (5, 0)
        )
        frm2 = engine_frame.addFrame(
            name         = 'Settings:frm2',
            widgetkwargs = {'style' : 'Dynamic.TFrame'},
            row          = 1,
            col          = 0,
            padx         = 0,
            pady         = 0
        )

        self.online_search_engine = self.settings['definitions']['search_engine']

        lbl = frm1.Label(text=f"({self.online_search_engine})", widgetkwargs = {'relief': tk.FLAT}, size=8, row=0, col=1)

        CwcButtonTkmt(
            master  = frm1,
            text    = gtbk('find_defs_online'),
            command = lambda lbl=lbl : self.__handle_find_defs_online(lbl=lbl),
            padx    = 8,
            row     = 0,
            col     = 0
        )

        frm2.Label(text=f"{GlobalData.DOWN_RIGHT_ARROW}{gtbk('add_text_to_search')}", widgetkwargs = {'relief': tk.FLAT}, size=8, row=0, col=0, padx=(20, 0), pady=0)
        frm2.Entry(textvariable=self.online_defs_search_add_words, row=0, col=1, widgetkwargs={'width': 50})

        self.online_defs_search_add_words.set(self.settings['definitions']['add_words'])

    def __create_editing_frame(self, main_frame:WidgetFrame):
        main_frame.Seperator(padx=10, pady=(10, 5), row=9, col=0, colspan=2)

        main_frame.Label(text=gtbk('word_editing'), size=10, row=10, col=0, colspan=2)

        main_frame.Checkbutton(text=gtbk('skip_black'), style='Switch.TCheckbutton', variable=GlobalData.SKIP_BLACK_CELLS, row=11, col=0, padx=5, pady=0)
        main_frame.Checkbutton(text=gtbk('auto_move') , style='Switch.TCheckbutton', variable=GlobalData.AUTO_MOVE       , row=12, col=0, padx=5, pady=0)

    def __create_appearance_frame(self, main_frame:WidgetFrame):
        main_frame.Seperator(padx=10, pady=(10, 5), row=13, col=0, colspan=2)

        main_frame.Label(text=gtbk('appearance'), size=10, row=14, col=0, colspan=2, pady=(0, 10))

        variables = {
            'theme_var'         : self.theme_var,
            'appearence_var'    : self.mode_var,
            'language_var'      : self.language_var,
            'arch_language_var' : self.arch_language_var
        }

        MenuFrame.create_style_frame(master=main_frame, frame_col=0, frame_row=15, variables=variables)

        self.theme_var.set(self.settings['appearance']['theme'])
        self.mode_var .set(self.settings['appearance']['mode'])

        # have to add a frame to contain the other 2 frames to set them near each other
        frame = ctk.CTkFrame(
            master       = main_frame.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0
        )
        frame.grid(row=15, column=1, padx=0, pady=0, sticky=tk.NS)
        wf = WidgetFrame(frame, name='')
        MenuFrame.create_languages_frame     (master=wf, frame_col=0, frame_row=0, variables=variables)
        MenuFrame.create_languages_join_frame(master=wf, frame_col=1, frame_row=0)

    def __create_buttons_frame(self, main_frame:WidgetFrame):
        main_frame.Seperator(padx=10, pady=(10, 5), row=16, col=0, colspan=2)

        bottom_frame = main_frame.addFrame(
            name         = 'Settings:bottom_frame',
            sticky       = tk.NSEW,
            padx         = 0,
            pady         = 0,
            row          = 17,
            col          = 0,
            colspan      = 2,
            use_tk       = True,
            widgetkwargs = {'relief' : tk.FLAT, 'borderwidth' : 0, 'background' : Colors.label_frame_col }
        )
        bottom_frame.master.grid_columnconfigure(0, weight=1)  # Center horizontally
        bottom_frame.master.grid_columnconfigure(1, weight=1)  # Center horizontally
        bottom_frame.master.grid_rowconfigure   (0, weight=1)  # Center vertically

        CwcButtonTkmt(
            master          = bottom_frame,
            image_base_name = 'save',
            command         = self.__save,
            padx            = 30,
            pady            = (0, 3),
            row             = 0,
            col             = 0,
            size            = 24,
            style           = 'Toolbutton'
        )
        CwcButtonTkmt(
            master          = bottom_frame,
            image_base_name = 'close',
            command         = self.window.quit,
            padx            = 30,
            pady            = (0, 3),
            row             = 0,
            col             = 1,
            size            = 24,
            style           = 'Toolbutton'
        )

    def __handle_find_defs_online(self, lbl, *_):
        with open(GlobalData.SEARCH_ENGINES_FILENAME, 'r', encoding='latin-1') as csvfile:
            r = csv.reader(csvfile, delimiter=';')
            names = [row[0] for row in r if row[0] != 'name']

        online_search_engine = InputPanel(title=f'{gtbk("find_defs_online")}', current_value='', suggested_values=names, allow_type=False).get_value()
        if online_search_engine != '':
            self.online_search_engine = online_search_engine
            lbl['text'] = f"({self.online_search_engine})"

    def __style_change(self):
        GlobalData.main_window.after(10, lambda : self.emit_style_change(style=self.theme_var.get(), mode=self.mode_var.get()))
        self.window.quit()

    def __save(self):
        GlobalData.TOT_ROWS          = self.cwc_templ.dimension_y.get()
        GlobalData.TOT_COLS          = self.cwc_templ.dimension_x.get()
        GlobalData.BLACK_PERCENT     = self.cwc_templ.amount_black_cells.get()
        GlobalData.CURRENT_FONT_SIZE = self.cwc_templ.font_size.get()
        GlobalData.MAX_WORD_LENGTH   = self.cwc_templ.max_word_len.get()

        self.settings['cw']['dim'           ] = [GlobalData.TOT_ROWS, GlobalData.TOT_COLS]
        self.settings['cw']['black_cells'   ] = get_black_cells_type(type_id=self.cwc_templ.black_cells_type.get())
        self.settings['cw']['random_percent'] = GlobalData.BLACK_PERCENT
        self.settings['cw']['font'          ] = GlobalData.CURRENT_FONT_SIZE
        self.settings['cw']['max_word_len'  ] = GlobalData.MAX_WORD_LENGTH

        self.settings['definitions']['hide_sel'     ] = GlobalData.CH_HIDE_VAR.get()
        self.settings['definitions']['auto_sel'     ] = GlobalData.CH_AUTO_SEL.get()
        self.settings['definitions']['add_words'    ] = self.online_defs_search_add_words.get()
        self.settings['definitions']['search_engine'] = self.online_search_engine

        self.settings['appearance']['theme'   ] = self.theme_var.get()
        self.settings['appearance']['mode'    ] = self.mode_var .get()
        self.settings['appearance']['language'] = get_language_code(language=self.language_var.get())

        self.settings['word_editing']['skip_black'] = GlobalData.SKIP_BLACK_CELLS.get()
        self.settings['word_editing']['auto_move']  = GlobalData.AUTO_MOVE.get()

        save_settings(settings=self.settings)

        if self.theme_var.get() != Theme.CURRENT_APP_THEME or self.mode_var.get() != Theme.CURRENT_APP_MODE:
            self.__style_change()

        VolatileMessage(text=gtbk('settings_saved'), center=True)

        self.window.quit()


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style
    set_style()
    s = Settings()
    bind(s, lambda *args, **kargs: print('emit_style_change'), 'emit_style_change')
    s.show()
