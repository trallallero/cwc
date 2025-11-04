"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to create all the main menu buttons.
"""

from tkinter import TOP

from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals  import (
    GlobalData,
    AppState,
    Colors
)
from cwc_button   import CwcButtonTkmt
from translations import gtbk

class MainButtons:
    """Class to create all the main menu buttons.
    It defines all the buttons' states for each application state.
    """

    __buttons: list[dict[str, CwcButtonTkmt]] = []

    __MAIN_BUTTONS = [
        {'key' : 'create'    , 'frame' : 'matrix' , 'command' : 'get_template'   , 'base_name' : 'plus'      , 'state' : 'normal'  , 'tt' : ''},
        {'key' : 'close'     , 'frame' : 'matrix' , 'command' : 'close_crossword', 'base_name' : 'close'     , 'state' : 'disabled', 'tt' : ''},
        {'key' : 'clear'     , 'frame' : 'matrix' , 'command' : 'clear_cw'       , 'base_name' : 'clear'     , 'state' : 'disabled', 'tt' : ''},
        {'key' : 'compile'   , 'frame' : 'matrix' , 'command' : 'fill_crossword' , 'base_name' : 'crossword' , 'state' : 'disabled', 'tt' : ''},
        {'key' : 'save'      , 'frame' : 'file'   , 'command' : 'save_project'   , 'base_name' : 'save'      , 'state' : 'disabled', 'tt' : gtbk('tt_save_pr')},
        {'key' : 'open'      , 'frame' : 'file'   , 'command' : 'open_project'   , 'base_name' : 'open'      , 'state' : 'normal'  , 'tt' : ''},
        {'key' : 'export'    , 'frame' : 'file'   , 'command' : 'export_cw'      , 'base_name' : 'export'    , 'state' : 'disabled', 'tt' : ''},
        {'key' : 'dimensions', 'frame' : 'options', 'command' : 'dimensions'     , 'base_name' : 'dimensions', 'state' : 'normal'  , 'tt' : ''},
        {'key' : 'settings'  , 'frame' : 'options', 'command' : 'settings'       , 'base_name' : 'settings'  , 'state' : 'normal'  , 'tt' : ''}
    ]

    __CW_NOT_CREATED_STATES = [
        {'key' : 'create'    , 'state' : 'normal'  },
        {'key' : 'close'     , 'state' : 'disabled'},
        {'key' : 'clear'     , 'state' : 'disabled'},
        {'key' : 'compile'   , 'state' : 'disabled'},
        {'key' : 'save'      , 'state' : 'disabled'},
        {'key' : 'open'      , 'state' : 'normal'  },
        {'key' : 'export'    , 'state' : 'disabled'}
    ]

    __CW_CREATED_STATES = [
        {'key' : 'create'    , 'state' : 'disabled'},
        {'key' : 'close'     , 'state' : 'normal'  },
        {'key' : 'clear'     , 'state' : 'disabled'},
        {'key' : 'compile'   , 'state' : 'disabled'},
        {'key' : 'save'      , 'state' : 'normal'  },
        {'key' : 'open'      , 'state' : 'disabled'},
        {'key' : 'export'    , 'state' : 'disabled'}
    ]

    __CW_FINALIZED_STATES = [
        {'key' : 'create'    , 'state' : 'disabled'},
        {'key' : 'close'     , 'state' : 'normal'  },
        {'key' : 'clear'     , 'state' : 'disabled'},
        {'key' : 'compile'   , 'state' : 'normal'  },
        {'key' : 'save'      , 'state' : 'normal'  },
        {'key' : 'open'      , 'state' : 'disabled'},
        {'key' : 'export'    , 'state' : 'disabled'}
    ]

    __CW_FILLED_STATES = [
        {'key' : 'create'    , 'state' : 'disabled'},
        {'key' : 'close'     , 'state' : 'normal'  },
        {'key' : 'clear'     , 'state' : 'normal'  },
        {'key' : 'compile'   , 'state' : 'normal'  },
        {'key' : 'save'      , 'state' : 'normal'  },
        {'key' : 'open'      , 'state' : 'disabled'},
        {'key' : 'export'    , 'state' : 'disabled'}
    ]

    __CW_COMPLETE_STATES = [
        {'key' : 'create'    , 'state' : 'disabled'},
        {'key' : 'close'     , 'state' : 'normal'  },
        {'key' : 'clear'     , 'state' : 'normal'  },
        {'key' : 'compile'   , 'state' : 'normal'  },
        {'key' : 'save'      , 'state' : 'normal'  },
        {'key' : 'open'      , 'state' : 'disabled'},
        {'key' : 'export'    , 'state' : 'normal'}
    ]

    @staticmethod
    def create_buttons(master, widget):
        wf_btns = WidgetFrame(master=master, name='main_frame_buttons')

        for col, item in enumerate(MainButtons.__MAIN_BUTTONS):
            btn = CwcButtonTkmt(
                master          = wf_btns,
                widget          = widget,
                text            = gtbk(item['key']),
                command_method  = item['command'],
                image_base_name = item['base_name'],
                row             = 0,
                col             = col,
                padx            = (10, 2) if col == 0 else (2, 10) if col == (len(MainButtons.__MAIN_BUTTONS)-1) else (2, 2),
                pady            = (3, 8),
                state           = item['state'],
                style           = 'Toolbutton',
                size            = 32,
                compound        = TOP,
                img_type        = 'cwc',
                tooltip         = item['tt']
            )
            MainButtons.__buttons.append({'key' : item['key'], 'btn' : btn})

    @staticmethod
    def enable_buttons(*_):
        match GlobalData.current_state():
            case AppState.AS_CW_NOT_CREATED       : values = MainButtons.__CW_NOT_CREATED_STATES
            case AppState.AS_CW_CREATED           : values = MainButtons.__CW_CREATED_STATES
            case AppState.AS_CW_FINALIZED         : values = MainButtons.__CW_FINALIZED_STATES
            case AppState.AS_CW_FILLED            : values = MainButtons.__CW_FILLED_STATES
            case AppState.AS_CW_COMPLETE          : values = MainButtons.__CW_COMPLETE_STATES
            case AppState.AS_BUSY|AppState.AS_NONE: values = []

        for v in values:
            key   = v['key']
            state = v['state']
            for b in MainButtons.__buttons:
                if b['key'] == key:
                    b['btn'].configure(state=state)
                    break


############# TESTS #############

if __name__ == "__main__":
    import customtkinter as ctk
    from cwc_style import set_style

    set_style()

    menu_frame_btns = ctk.CTkFrame(
            master       = GlobalData.main_window,
            fg_color     = str(Colors.label_frame_col),
            bg_color     = 'transparent',
            border_width = 0,
        )
    menu_frame_btns.grid(row=0, column=0)
    menu_frame_btns.grid_rowconfigure   (0, weight=1)
    menu_frame_btns.grid_columnconfigure(0, weight=1)

    MainButtons.create_buttons(master=menu_frame_btns, widget=None)
    GlobalData.main_window.mainloop()
