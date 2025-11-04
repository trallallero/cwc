"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.

Module to create the application's top level widgets"""

import os
import inspect
import tkinter as tk
import TKinterModernThemes as TKMT

from cwc_globals import (
    GlobalData,
    Colors,
    center_window,
    set_window_to_mouse_point
)

class CwcTopLevel(TKMT.ThemedTKinterFrame):
    """Class to create the application's top level widgets"""

    cancel = False

    def __init__(
            self,
            create_frame = True,  # True centers to parent, False to mouse point
            title        = '',
            center       = True,
            focus        = True,  # True means grab events
            margin       = False, # See GlobalData.POPUP_MENU_WINDOW_MARGIN
            bind_esc     = True   # True means quit on Esc press
        ):
        super().__init__(title=title,usecommandlineargs=False, useconfigfile=False)

        self.center = center
        self.focus  = focus
        self.margin = margin

        self.root.overrideredirect(True)

        if bind_esc:
            self.root.bind('<Escape>', lambda _: self.quit(cancel=True))

        if create_frame:
            border_frame = self.addFrame(name='CwcTopLevel:border_frame', widgetkwargs={'style' : 'CwcTopLevel.TFrame'}, padx=0, pady=0)
            self.__frame = border_frame.addFrame(name='CwcTopLevel:root', use_tk=True, widgetkwargs={'relief' : tk.FLAT, 'borderwidth' : 0, 'background' : Colors.label_frame_col}, padx=2, pady=2)
        else:
            self.__frame = self.addFrame(name='CwcTopLevel:root', widgetkwargs={'style' : 'Transp.TFrame'}, padx=0, pady=0)

        if focus:
            self.root.focus_set()

    def show(self, modify_x=0, modify_y=0, center_to_screen=False):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        CwcTopLevel.cancel = False
        if self.focus:
            self.root.grab_set()
            self.root.focus_set()
        self.__position_win(modify_x=modify_x, modify_y=modify_y, center_to_screen=center_to_screen)
        self.root.deiconify()
        if self.focus:
            self.root.mainloop() # dont'call self.run() bc it centers window to screen
        else:
            self.root.update()

    def quit(self, cancel=False, _='', __=''):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if self.focus:
            CwcTopLevel.cancel = cancel
            if self.root != GlobalData.main_tkmt_window:
                self.handleExit()
        else:
            self.root.withdraw()
            del self

    def frame(self):
        return self.__frame

    def __position_win(self, modify_x, modify_y, center_to_screen=False):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if self.center:
            center_window(win=self.root, to_screen=center_to_screen)
        else:
            set_window_to_mouse_point(win=self.root, modify_x=modify_x, modify_y=modify_y, margin=self.margin)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    window      = CwcTopLevel(title='top_level', create_frame=True, margin=True)
    window.frame().Label(text="just a test 1", padx=0, pady=0)
    f = window.frame().addLabelFrame("Test")
    f.Button(text="click", command=None)
    set_style()
    window.run()
