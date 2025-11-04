"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

This code is based on tkinter-tooltip (c) gnikit, MIT License.
See LICENSE for details - https://github.com/gnikit/tkinter-tooltip
----

Module defining custom button classes for the application."""

import os
import tkinter as tk
from PIL import Image, ImageTk

from tktooltip import ToolTip

from TKinterModernThemes.WidgetFrame import WidgetFrame

from customtkinter import CTkButton

from cwc_globals import (
    AppState,
    Colors,
    GlobalData,
    get_internal_image,
    get_forbid_curs,
    get_translation_by_key,
    bind
)

from translations import (
    gkbv,
    gtbk
)


class CwcButton:
    """Class for the base handling of the CwcButtons.
    It mainly handles the ToolTip and language change.
    """
    __buttons = []

    def __init__(self, tooltip):
        self.tooltip     = None
        self.tooltip_msg = tooltip

        if tooltip != '':
            self.tooltip = ToolTip(
                widget = self.get_button(),
                msg    = self.tooltip_msg,
                delay  = GlobalData.TOOLTIP_OPEN_TIME_MS
            )

        if len(CwcButton.__buttons) == 0:
            bind(GlobalData, CwcButton.on_language_change, 'emit_change_language')

        CwcButton.__buttons.append(self)

    def __del__(self):
        CwcButton.__buttons.remove(self)

    @staticmethod
    def on_language_change(*_, language):
        for b in CwcButton.__buttons:
            b.change_language(language=language)

    def get_button(self):
        return None

    def change_language(self, language):
        if self.tooltip_msg == '':
            return

        # Get the translation key from the current tooltip message and then
        # get the translated message with the new language.
        # A bit expensive but how often does the user change the language?
        key = gkbv(self.tooltip_msg)
        self.tooltip_msg = get_translation_by_key(key=key, lang=language)

        if self.tooltip:
            del self.tooltip

        self.tooltip = ToolTip(
            widget = self.get_button(),
            msg    = self.tooltip_msg,
            delay  = GlobalData.TOOLTIP_OPEN_TIME_MS
        )


class CwcButtonCtk(CTkButton, CwcButton):
    """Class defining custom button based on CTkButton for the application."""

    def __init__(self,
        master              = None,
        text:str            = '',
        text_color          = (Colors.black, Colors.black),
        command             = None,
        image_base_name:str = '',
        row:int             = 0,
        col:int             = 0,
        padx:int            = 0,
        pady:int            = 0,
        fg_color            = 'transparent',
        hover_color         = None,
        hover               = False,
        sticky              = tk.NS,
        state:str           = 'disabled',
        compound            = tk.TOP,
        size                = 20,
        border_width        = 0,
        anchor              = tk.E,
        cursor              = get_forbid_curs(),
        tooltip             = ''
    ):
        super().__init__(
            master          = master,
            text            = text,
            text_color      = text_color,
            width           = size,
            height          = size,
            fg_color        = fg_color,
            hover_color     = hover_color,
            hover           = hover,
            image           = get_internal_image(base_name=image_base_name, size=size) if image_base_name else None,
            state           = state,
            border_width    = border_width,
            border_color    = Colors.blue,
            compound        = compound,
            command         = command,
            anchor          = anchor,
            cursor          = cursor
        )
        CwcButton.__init__(self, tooltip=tooltip)

        self.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)

    def get_button(self):
        return self


class CwcButtonTkmt(CwcButton):
    """Class defining custom button based on TKinterModernThemes for the application."""

    def __init__(
        self,
        master:WidgetFrame  = None,
        widget              = None,
        text:str            = '',
        command             = None,
        command_method:str  = '',
        image_base_name:str = '',
        row:int             = 0,
        col:int             = 0,
        padx:int            = 0,
        pady:int            = 0,
        sticky              = tk.NS,
        state:str           = 'normal',
        style               = 'Toggle.TButton',
        compound            = tk.CENTER,
        size                = 16,
        rowspan             = 1,
        columnspan          = 1,
        img_type            = '',
        busy_is_disabled    = True, # True means if app is busy, cursor is busy
        tooltip             = ''
    ):
        if image_base_name != '':
            image    = Image.open(os.path.join(GlobalData.ROOT_DIR, f'images/{img_type}/{image_base_name}.png')).resize((size, size))
            self.img = ImageTk.PhotoImage(image)
        else:
            self.img = None

        self._btn = master.Button(
            text            = text,
            command         = getattr(widget, command_method) if command_method != '' and widget else command,
            row             = row,
            col             = col,
            padx            = padx,
            pady            = pady,
            sticky          = sticky,
            style           = style,
            rowspan         = rowspan,
            colspan         = columnspan,
            widgetkwargs    = {'state' : state, 'image' : self.img, 'compound' : compound, 'width' : 0}
        )
        self.busy_is_disabled = busy_is_disabled

        CwcButton.__init__(self, tooltip=tooltip)

        self._btn.bind('<Enter>', self.__highlight, add='+')

    def get_button(self):
        return self._btn

    def configure(self, **kwargs):
        self._btn.configure(kwargs)

    def __highlight(self, *_):
        if self.busy_is_disabled and GlobalData.current_state() == AppState.AS_BUSY:
            self._btn.configure(cursor='watch')
        elif str(self._btn.cget('state')) == 'normal':
            self._btn.configure(cursor='hand2')
        else:
            self._btn.configure(cursor=get_forbid_curs())


################# TESTS ##################

if __name__ == "__main__":
    from cwc_style import set_style
    from cwc_toplevel import CwcTopLevel

    set_style()

    window = CwcTopLevel(title='top_level')
    #CwcButtonCtk(master=window.frame().master, image_base_name='add', state='normal'  , text='enabled' , row=0, col=0, tooltip=gtbk('test'))
    #CwcButtonCtk(master=window.frame().master, image_base_name='add', state='disabled', text='disabled', row=0, col=1, tooltip=gtbk('test'))
    CwcButtonTkmt(
        master          = window.frame(),
        text            = gtbk('test'),
        image_base_name = 'save',
        command         = None,
        row             = 1,
        col             = 0,
        sticky          = tk.EW,
        style           = 'Toolbutton',
        compound        = tk.LEFT,
        state           = 'normal',
        tooltip         = gtbk('test')
    )
    CwcButtonTkmt(
        master          = window.frame(),
        text            = 'test2',
        image_base_name = 'save',
        command         = None,
        row             = 1,
        col             = 1,
        sticky          = tk.EW,
        style           = 'Toolbutton',
        compound        = tk.LEFT,
        state           = 'disabled',
        tooltip         = gtbk('test')
    )
    window.show()
