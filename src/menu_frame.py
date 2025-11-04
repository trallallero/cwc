"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module for the application's main menu handling."""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals import (
    Theme,
    GlobalData,
    Colors,
    get_language,
    change_language,
    get_language_code,
    bind
)

from about        import About
from main_buttons import MainButtons
from cwc_button   import (
    CwcButtonCtk,
    CwcButtonTkmt
)
from translations import (
    gtbk,
    get_languages
)

class MenuFrame:
    """Class for the application's main menu handling.
    All static indipendent methods to allow the creation of the single menus,
    when needed (e.g. from Settings module).
    """

    __JOIN_LANG_LBL:WidgetFrame.Label = None
    __LANG_LBL     :WidgetFrame.Label = None
    __DB_LANG_LBL  :WidgetFrame.Label = None
    __LANGUAGE_VAR                    = tk.StringVar()
    __ARCHIVE_VAR                     = tk.StringVar()
    __CBMODE_ARCH:str                 = ''
    __JOIN_LANGS:bool                 = True
    __CURRENT_COL:int                 = -1


    @staticmethod
    def create(master:WidgetFrame, widget, variables):
        MenuFrame.create_buttons_frame(master=master, widget=widget, frame_col=MenuFrame.__get_next_col())
        master.Seperator(row=0, col=MenuFrame.__get_next_col(), sticky=tk.NS, padx=0, pady=3)

        MenuFrame.create_definitions_frame(master=master, frame_col=MenuFrame.__get_next_col())
        master.Seperator(row=0, col=MenuFrame.__get_next_col(), sticky=tk.NS, padx=0, pady=3)

        MenuFrame.create_style_frame(master=master, frame_col=MenuFrame.__get_next_col(), variables=variables)
        master.Seperator(row=0, col=MenuFrame.__get_next_col(), sticky=tk.NS, padx=0, pady=3)

        MenuFrame.create_languages_frame(master=master, frame_col=MenuFrame.__get_next_col())
        MenuFrame.create_languages_join_frame(master=master, frame_col=MenuFrame.__get_next_col(), internal=True)
        master.Seperator(row=0, col=MenuFrame.__get_next_col(), sticky=tk.NS, padx=0, pady=3)

        MenuFrame.create_scale_frame(master=master, frame_col=MenuFrame.__get_next_col(), variables=variables)

        master.Seperator(row=0, col=MenuFrame.__get_next_col(), sticky=tk.NS, padx=0, pady=3)

        MenuFrame.create_about_frame(master=master, frame_col=MenuFrame.__get_next_col())

        MenuFrame.__trace_vars()

        MenuFrame.__finalize(master=master)

    @staticmethod
    def create_buttons_frame(master:WidgetFrame, widget, frame_col, frame_row=0):
        menu_frame_btns = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        menu_frame_btns.grid(row=frame_row, column=frame_col, sticky=tk.NS)
        menu_frame_btns.grid_rowconfigure   (0, weight=1)
        menu_frame_btns.grid_columnconfigure(0, weight=1)

        MainButtons.create_buttons(master=menu_frame_btns, widget=widget)
        return menu_frame_btns

    @staticmethod
    def create_definitions_frame(master:WidgetFrame, frame_col, frame_row=0, create_title=True):
        menu_frame_defs = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        menu_frame_defs.grid(row=frame_row, column=frame_col, sticky=tk.NS)
        menu_frame_defs.grid_rowconfigure   (0, weight=0)
        menu_frame_defs.grid_rowconfigure   (1, weight=0)
        menu_frame_defs.grid_columnconfigure(0, weight=0)

        wf_chks = WidgetFrame(menu_frame_defs, name='')
        if create_title:
            wf_chks.Label(text=gtbk('definitions'), size=10, row=0, col=0, weight='normal', padx=0, pady=(0, 5))
        wf_chks.Checkbutton(text=gtbk('hide_def'), style='Switch.TCheckbutton', variable=GlobalData.CH_HIDE_VAR, widgetkwargs={'offvalue' : False, 'onvalue' : True}, row=1, col=0, pady=0)
        wf_chks.Checkbutton(text=gtbk('auto_sel'), style='Switch.TCheckbutton', variable=GlobalData.CH_AUTO_SEL, widgetkwargs={'offvalue' : False, 'onvalue' : True}, row=2, col=0, pady=0)
        return menu_frame_defs

    @staticmethod
    def create_style_frame(master:WidgetFrame, variables, frame_col, frame_row=0):
        menu_frame_style = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        menu_frame_style.grid(row=frame_row, column=frame_col, sticky=tk.NE)

        wf_style = WidgetFrame(menu_frame_style, name='')
        wf_style.Label(text=gtbk('style'), size=8, row=0, col=0, sticky=tk.NW)
        wf_style.Combobox(
            values       = Theme.APP_THEMES,
            variable     = variables['theme_var'],
            row          = 0,
            col          = 1,
            padx         = (0,10),
            pady         = 1,
            widgetkwargs = {
                'style'   : 'Custom.TCombobox',
                'state'   : 'readonly',
                'font'    : GlobalData.SMALL_COMBO_FONT,
                'height'  : len(Theme.APP_THEMES),
                'width'   : 10
            }
        )

        wf_style.Label(text=gtbk('appearance'), size=8, row=1, col=0, sticky=tk.NW)
        wf_style.Combobox(
            values       = Theme.APP_MODES,
            variable     = variables['appearence_var'],
            row          = 1,
            col          = 1,
            padx         = (0,10),
            pady         = 1,
            widgetkwargs = {
                'style'   : 'Custom.TCombobox',
                'state'   : 'readonly',
                'font'   : GlobalData.SMALL_COMBO_FONT,
                'height' : len(Theme.APP_MODES),
                'width'  : 10
            }
        )
        return menu_frame_style

    @staticmethod
    def create_languages_frame(master:WidgetFrame, frame_col, frame_row=0, variables=None):
        menu_frame_lang = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0
        )
        menu_frame_lang.grid(row=frame_row, column=frame_col, sticky=tk.NE)
        menu_frame_lang.grid_rowconfigure(0, weight=0)
        menu_frame_lang.grid_columnconfigure(0, weight=0)
        menu_frame_lang.grid_columnconfigure(1, weight=0)

        wf_lang = WidgetFrame(menu_frame_lang, name='')

        wf_lang.Label(text=gtbk('language'), size=8, row=0, col=0, padx=(10, 3), sticky=tk.W)
        wf_lang.Combobox(
            values       = get_languages(),
            variable     = MenuFrame.__LANGUAGE_VAR if not variables else variables['language_var'],
            row          = 0,
            col          = 1,
            padx         = (0,1),
            pady         = 1,
            widgetkwargs = {
                'style'   : 'Custom.TCombobox',
                'state'   : 'readonly',
                'font'    : GlobalData.SMALL_COMBO_FONT,
                'height'  : len(Theme.APP_THEMES),
                'width'   : 10
            }
        )
        if not variables:
            MenuFrame.__LANGUAGE_VAR.set(get_language(code=GlobalData.CURRENT_LANGUAGE))

        wf_lang.Label(text=gtbk('database_language'), size=8, row=1, col=0, padx=(10, 3), sticky=tk.W)
        wf_lang.Combobox(
            values       = get_languages(),
            variable     = MenuFrame.__ARCHIVE_VAR if not variables else variables['arch_language_var'],
            row          = 1,
            col          = 1,
            padx         = (0,1),
            pady         = 1,
            widgetkwargs = {
                'style'   : 'Custom.TCombobox',
                'state'   : 'readonly',
                'font'    : GlobalData.SMALL_COMBO_FONT,
                'height'  : len(Theme.APP_THEMES),
                'width'   : 10
            }
        )
        if not variables:
            MenuFrame.__ARCHIVE_VAR.set(get_language(code=GlobalData.CURRENT_ARCHIVE_LANGUAGE))
        menu_frame_lang.grid_columnconfigure(2, weight=0)

        if variables:
            variables['language_var'     ].set(get_language(code=GlobalData.CURRENT_LANGUAGE))
            variables['arch_language_var'].set(get_language(code=GlobalData.CURRENT_ARCHIVE_LANGUAGE))
            MenuFrame.__trace_external_vars(lang_var=variables['language_var'], arch_var=variables['arch_language_var'])

        return menu_frame_lang

    @staticmethod
    def create_languages_join_frame(master:WidgetFrame, frame_col, frame_row=0, internal=False):
        menu_frame_lang_join = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0
        )
        menu_frame_lang_join.grid(row=frame_row, column=frame_col, sticky=tk.EW)
        menu_frame_lang_join.grid_rowconfigure(0, weight=0)
        menu_frame_lang_join.grid_rowconfigure(1, weight=0)
        menu_frame_lang_join.grid_rowconfigure(2, weight=0)
        menu_frame_lang_join.grid_columnconfigure(0, weight=0)

        wf_lang_join = WidgetFrame(menu_frame_lang_join, name='')

        lang_lbl      = wf_lang_join.Label(text=GlobalData.UP_JOIN_ARROW  , size=12, row=0, col=0, padx=(0, 3), pady=0, sticky=tk.W)
        join_lang_lbl = wf_lang_join.Label(text=GlobalData.DOUBLE_VERTICAL, size=12, row=1, col=0, padx=(0, 3), pady=0, sticky=tk.W)
        db_lang_lbl   = wf_lang_join.Label(text=GlobalData.DOWN_JOIN_ARROW, size=12, row=2, col=0, padx=(0, 3), pady=0, sticky=tk.W)

        join_lang_lbl.configure(cursor='hand2')
        join_lang_lbl.bind(
            '<Button>',
            lambda event, internal=internal, lbls=(join_lang_lbl, lang_lbl, db_lang_lbl) :
                MenuFrame.__on_join_langs(internal=internal, lbls=lbls))

        if internal:
            MenuFrame.__JOIN_LANG_LBL = join_lang_lbl
            MenuFrame.__LANG_LBL      = lang_lbl
            MenuFrame.__DB_LANG_LBL   = db_lang_lbl
        else:
            MenuFrame.__on_join_langs(internal=internal, lbls=(join_lang_lbl, lang_lbl, db_lang_lbl), refresh=True)

        return menu_frame_lang_join

    @staticmethod
    def create_scale_frame(master:WidgetFrame, variables, frame_col, frame_row=0):
        menu_frame_scale = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        menu_frame_scale.grid(row=frame_row, column=frame_col, sticky=tk.NE)
        menu_frame_scale.grid_rowconfigure   (0, weight=0)
        menu_frame_scale.grid_rowconfigure   (1, weight=0)
        menu_frame_scale.grid_columnconfigure(0, weight=0)
        menu_frame_scale.grid_columnconfigure(1, weight=0)
        menu_frame_scale.grid_columnconfigure(2, weight=0)

        wf_scale = WidgetFrame(master=menu_frame_scale, name='main_frame_checkbuttons')
        wf_scale.Label(text=gtbk('resize'), size=10, row=0, col=0, colspan=3, weight='normal')

        CwcButtonCtk(
            master          = wf_scale.master,
            command         = lambda :
                MenuFrame.__on_resize(less_more='less', var=variables['resize_var']),
            text            = GlobalData.LEFT_DOUBLE_ARROW,
            row             = 1,
            col             = 0,
            padx            = 0,
            pady            = 0,
            state           = 'normal',
            size            = 12,
            compound        = tk.TOP,
            cursor          = 'hand2'
        )

        wf_scale.Scale(
            sticky       = tk.NSEW,
            lower        = 2,
            upper        = GlobalData.RESIZE_MAX_VALUE,
            variable     = variables['resize_var'],
            padx         = 0,
            pady         = 3,
            row          = 1,
            col          = 1,
            widgetkwargs = {'length' : 100, 'takefocus' : True, 'style' : 'Horizontal.TScale', 'cursor' : 'hand2'}
        )

        CwcButtonCtk(
            master          = wf_scale.master,
            command         = lambda :
                MenuFrame.__on_resize(less_more='more', var=variables['resize_var']),
            text            = GlobalData.RIGHT_DOUBLE_ARROW,
            row             = 1,
            col             = 2,
            padx            = 0,
            pady            = 0,
            state           = 'normal',
            size            = 12,
            compound        = tk.TOP,
            cursor          = 'hand2'
        )
        return menu_frame_scale

    @staticmethod
    def create_about_frame(master:WidgetFrame, frame_col):
        about_frame = ctk.CTkFrame(
            master       = master.master,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
        about_frame.grid(row=0, column=frame_col, sticky=tk.NSEW)
        about_frame.grid_rowconfigure   (0, weight=1)
        about_frame.grid_columnconfigure(0, weight=0)

        wf_scale = WidgetFrame(master=about_frame, name='about_frame')

        CwcButtonTkmt(
            master          = wf_scale,
            command         = MenuFrame.__show_about,
            text            = gtbk('about'),
            row             = 0,
            col             = 0,
            padx            = 5,
            pady            = 10,
            state           = 'normal',
            style           = 'Toolbutton',
            size            = 12
        )

    @staticmethod
    def __show_about():
        About().show()

    @staticmethod
    def __finalize(master):
        master.master.grid_rowconfigure(0, weight=0)
        last_col = MenuFrame.__get_next_col(current=True)
        for col in range(last_col):
            master.master.grid_columnconfigure(col, weight=0)

        master.master.grid_columnconfigure(last_col, weight=1)

        bind(GlobalData, MainButtons.enable_buttons, 'emit_state_changed')

    @staticmethod
    def __on_join_langs(internal, lbls:tuple[ttk.Label, ttk.Label, ttk.Label], refresh=False):
        if refresh:
            MenuFrame.__JOIN_LANGS = not MenuFrame.__JOIN_LANGS
            MenuFrame.__on_join_langs(internal=internal, lbls=lbls, refresh=False)
        elif MenuFrame.__JOIN_LANGS:
            MenuFrame.__JOIN_LANGS = False

            lbls[0].configure(text=GlobalData.DOUBLE_HORIZONTAL)
            lbls[1].configure(foreground=Colors.grey)
            lbls[2].configure(foreground=Colors.grey)
            if not internal:
                if MenuFrame.__JOIN_LANG_LBL:
                    MenuFrame.__JOIN_LANG_LBL.configure(text=GlobalData.DOUBLE_HORIZONTAL)
                if MenuFrame.__LANG_LBL:
                    MenuFrame.__LANG_LBL.configure(foreground=Colors.grey)
                if MenuFrame.__DB_LANG_LBL:
                    MenuFrame.__DB_LANG_LBL.configure(foreground=Colors.grey)
        else:
            MenuFrame.__JOIN_LANGS = True
            lbls[0].configure(text=GlobalData.DOUBLE_VERTICAL)
            lbls[1].configure(foreground=Colors.white if Theme.CURRENT_APP_MODE == 'dark' else Colors.black)
            lbls[2].configure(foreground=Colors.white if Theme.CURRENT_APP_MODE == 'dark' else Colors.black)
            if not internal:
                if MenuFrame.__JOIN_LANG_LBL:
                    MenuFrame.__JOIN_LANG_LBL.configure(text=GlobalData.DOUBLE_VERTICAL)
                if MenuFrame.__LANG_LBL:
                    MenuFrame.__LANG_LBL.configure(foreground=Colors.white)
                if MenuFrame.__DB_LANG_LBL:
                    MenuFrame.__DB_LANG_LBL.configure(foreground=Colors.white)

    @staticmethod
    def __on_language_change(lang_var, arch_var):
        if MenuFrame.__JOIN_LANGS:
            arch_var.trace_remove('write', MenuFrame.__CBMODE_ARCH if arch_var == MenuFrame.__ARCHIVE_VAR else MenuFrame.CBMODE_ARCH_EXT)
            arch_var.set(lang_var.get())
            cbmode_arch = arch_var.trace_add(
                'write',
                lambda event, *_ : MenuFrame.__on_archive_language_change(
                    lang_var = lang_var,
                    arch_var = arch_var
                )
            )
            if arch_var == MenuFrame.__ARCHIVE_VAR:
                MenuFrame.__CBMODE_ARCH = cbmode_arch
            else:
                MenuFrame.CBMODE_ARCH_EXT = cbmode_arch

        change_language(get_language_code(language=lang_var.get()))

    @staticmethod
    def __on_archive_language_change(lang_var, arch_var):
        if MenuFrame.__JOIN_LANGS:
            lang_var.set(arch_var.get())
        GlobalData.CURRENT_ARCHIVE_LANGUAGE = get_language_code(language=arch_var.get())

    @staticmethod
    def __on_resize(less_more, var):
        if not var:
            return

        if less_more == 'more' and var.get() < GlobalData.RESIZE_MAX_VALUE:
            var.set(var.get() + 1)
        elif less_more == 'less' and var.get() > GlobalData.RESIZE_MIN_VALUE:
            var.set(var.get() - 1)

    @staticmethod
    def __trace_vars():
        MenuFrame.__LANGUAGE_VAR.trace_add(
            'write',
            lambda event, *_ : MenuFrame.__on_language_change(
                lang_var = MenuFrame.__LANGUAGE_VAR,
                arch_var = MenuFrame.__ARCHIVE_VAR
            )
        )
        MenuFrame.__CBMODE_ARCH = MenuFrame.__ARCHIVE_VAR.trace_add(
            'write',
            lambda event, *_ : MenuFrame.__on_archive_language_change(
                lang_var = MenuFrame.__LANGUAGE_VAR,
                arch_var = MenuFrame.__ARCHIVE_VAR
            )
        )

    @staticmethod
    def __trace_external_vars(lang_var, arch_var):
        lang_var.trace_add('write', lambda *_:
            (
                MenuFrame.__LANGUAGE_VAR.set(lang_var.get()),
                MenuFrame.__on_language_change(lang_var=lang_var, arch_var=arch_var)
            )
        )
        MenuFrame.CBMODE_ARCH_EXT = arch_var.trace_add('write', lambda *_:
            (
                MenuFrame.__ARCHIVE_VAR.set(arch_var.get()),
                MenuFrame.__on_archive_language_change(lang_var=lang_var, arch_var=arch_var)
            )
        )

    @staticmethod
    def __get_next_col(current=False):
        if not current:
            MenuFrame.__CURRENT_COL += 1
        return MenuFrame.__CURRENT_COL


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    wf = WidgetFrame(master=GlobalData.main_window, name='')
    class _test:
        def get_template(self):
            pass
        def clear_cw(self):
            pass
        def fill_crossword(self):
            pass
        def close_crossword(self):
            pass
        def save_project(self):
            pass
        def open_project(self):
            pass
        def export_cw(self):
            pass
        def dimensions(self):
            pass
        def settings(self):
            pass

    set_style()

    MenuFrame.create(
        master    = wf,
        widget    = _test(),
        variables = {'theme_var' : None, 'resize_var' : None, 'appearence_var' : None }
    )
    GlobalData.main_tkmt_window.run()
