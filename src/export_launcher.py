"""Module to run crossword exporter plugins.
To add an exporter plugin, one has to add:
- a file <type>_exporter.py (type is lowercase) in GlobalData.PLUGINS_DIR
- in that file, a class <type>Exporter (type is capitalized)
- in that class, a public method 'def export(self, filename)' has to be implemented
"""

import os
import sys
import glob
from pathlib import Path

import tkinter as tk
import filedialpy

from cwc_globals import (
    GlobalData,
    bind
)
from cwc_toplevel     import CwcTopLevel
from cwc_button       import CwcButtonTkmt
from app_thread_executor     import AppThreadExecutor
from volatile_message import VolatileMessage
from translations     import gtbk

app_dir    = os.path.abspath(os.path.dirname(__file__))
plugin_dir = os.path.join(app_dir, GlobalData.PLUGINS_DIR)
sys.path.append(plugin_dir)


class ExportLauncher:
    def __init__(self) -> None:
        self.window       = CwcTopLevel(center=False, focus=True)
        self.cb_type      = None
        self.current_type = tk.StringVar()

    def show(self):
        self.window.frame().Label(text=gtbk('format'), size=GlobalData.FONT_SMALL_SIZE, row=0, col=0, colspan=2)

        self.cb_type = self.window.frame().Combobox(
            values       = self.__get_plugin_types(),
            variable     = self.current_type,
            padx         = 5,
            pady         = 5,
            row          = 1,
            col          = 0,
            colspan      = 2,
            widgetkwargs = {
                'width' : 5,
                'font'  : GlobalData.SMALL_COMBO_FONT,
                'state' : 'readonly'
            }
        )

        CwcButtonTkmt(
            master          = self.window.frame(),
            image_base_name = 'save',
            command         = self.__export,
            row             = 2,
            col             = 0,
            padx            = 10,
            pady            = 5
        )
        CwcButtonTkmt(
            master          = self.window.frame(),
            image_base_name = 'close',
            command         = self.window.quit,
            row             = 2,
            col             = 1,
            padx            = 10,
            pady            = 5
        )
        self.window.show()

    def __get_plugin_types(self):
        types = []
        for file in glob.glob('plugins/*exporter.py'):
            file = Path(file).stem
            if '_' in file:
                types.append(file.split(sep='_')[0])
        return types

    def __export(self, *_):
        _type    = self.current_type.get()
        filename = ExportLauncher.__get_filename(_type=_type)
        if filename == '':
            return

        print(filename)

        try:
            with AppThreadExecutor(
                method      = lambda _type=_type, filename=filename: ExportLauncher.__export_internal(_type=_type, filename=filename),
                show_cancel = False,
                message_key = 'exporting',
                send_emits  = False
            ): GlobalData.main_window.after(300, lambda : VolatileMessage(text=gtbk('exported')))
        except Exception as e:
            GlobalData.main_window.after(300, lambda : VolatileMessage(text=f'ERROR\n{str(e)}'))

        self.window.quit()

    @staticmethod
    def __get_filename(_type):
        return str(filedialpy.saveFile(title=gtbk('select_file'), initial_dir=GlobalData.DIRNAME, filter=f'*.{_type}'))

    @staticmethod
    def __export_internal(_type:str, filename):
        exporter_module = __import__(f'{_type.lower()}_exporter')
        exporter_class  = getattr(exporter_module, f'{_type.title()}Exporter')
        exporter_class().export(filename=filename)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    bind(GlobalData , lambda *_ : print(''), 'emit_state_changed')
    bind(AppThreadExecutor, lambda *_ : print(''), 'emit_started' )
    bind(AppThreadExecutor, lambda *_ : print(''), 'emit_finished')

    set_style()

    et = ExportLauncher()
    et.show()
