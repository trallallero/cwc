"""
This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to handle the DefinitionElement.

TODO:
- move ElementData class to a new file
- document it
"""

import os
import inspect
import random
from enum import Enum

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from cwc_globals import (
    GlobalData,
    AppState,
    Colors,
    Direction,
    bind,
    all_children,
    get_parent_widget
)
from highlighter  import Highlighter
from cell_handler import CellHandler
from word         import Word
from app_thread_executor import AppThreadExecutor
from cwc_matrix  import CwcMatrix, MatrixType

class FrameState(Enum):
    FS_BUSY                = 0
    FS_UNBUSY              = 1
    FS_EMPTY               = 2
    FS_WORD_SET_NOT_EXISTS = 3
    FS_WORD_SET_EXISTS     = 4
    FS_COMPLETE            = 5

    @staticmethod
    def get_dark_color_by_state(state):
        match state:
            case FrameState.FS_EMPTY:
                return Colors.dark_red
            case FrameState.FS_WORD_SET_NOT_EXISTS:
                return Colors.dark_red
            case FrameState.FS_WORD_SET_EXISTS:
                return Colors.dark_yellow
            case FrameState.FS_COMPLETE:
                return Colors.dark_green

    @staticmethod
    def get_light_color_by_state(state):
        match state:
            case FrameState.FS_EMPTY:
                return Colors.light_red
            case FrameState.FS_WORD_SET_NOT_EXISTS:
                return Colors.light_red
            case FrameState.FS_WORD_SET_EXISTS:
                return Colors.light_yellow
            case FrameState.FS_COMPLETE:
                return Colors.light_green

class ForceOpenType(Enum):
    FOT_NONE    = 0
    FOT_OPEN    = 1
    FOT_CLOSE   = 2
    FOT_REFRESH = 3

class ElementData:
    def __init__(self):
        self.__word:Word                           = None
        self.__row:int                             = None
        self.__parent_frame:ctk.CTkScrollableFrame = None
        self.__main_frame:ctk.CTkFrame             = None
        self.__hiding_frame:ctk.CTkFrame           = None
        self.__lbl_word:ctk.CTkLabel               = None
        self.__lbl_def:ctk.CTkLabel                = None
        self.__lbl_frame:ctk.CTkLabel              = None
        self.__listbox:tk.Listbox                  = None
        self.__frame_state:FrameState              = FrameState.FS_EMPTY

    def get_parent(self):
        return self.__parent_frame

    def clear(self):
        self.set_state(state=FrameState.FS_EMPTY)

    def get_word(self):
        return self.__word

    def get_state(self):
        return self.__frame_state

    def get_data(self, key:str):
        match key:
            case 'word'          : return self.__word
            case 'row'           : return self.__row
            case 'parent_frame'  : return self.__parent_frame
            case 'main_frame'    : return self.__main_frame
            case 'hiding_frame'  : return self.__hiding_frame
            case 'lbl_word'      : return self.__lbl_word
            case 'lbl_def'       : return self.__lbl_def
            case 'lbl_frame'     : return self.__lbl_frame
            case 'listbox'       : return self.__listbox
            case 'frame_state'   : return self.__frame_state
            case _               : return None

    def set_data(self, key:str, data):
        match key:
            case 'word'          : self.__word         = data
            case 'row'           : self.__row          = data
            case 'parent_frame'  : self.__parent_frame = data
            case 'main_frame'    : self.__main_frame   = data
            case 'hiding_frame'  : self.__hiding_frame = data
            case 'lbl_word'      : self.__lbl_word     = data
            case 'lbl_def'       : self.__lbl_def      = data
            case 'lbl_frame'     : self.__lbl_frame    = data
            case 'listbox'       : self.__listbox      = data
            case 'frame_state'   : self.__frame_state  = data
            case _               : pass

    def set_state(self, state:FrameState, highlighted:bool = False, definition=None):
        print(f'setting state "{state.name}" to word "{self.__word.get_word()}"')

        match state:
            case FrameState.FS_BUSY:
                self.__lbl_def   .configure(cursor='watch')
                self.__lbl_frame .configure(cursor='watch')
                self.__lbl_word  .configure(cursor='watch')
                self.__listbox   .configure(cursor='watch')
                self.__main_frame.configure(cursor='watch')
                return
            case FrameState.FS_UNBUSY:
                return
            case FrameState.FS_EMPTY:
                self.__clear_listbox()
                self.open_close_hiding_frame(force=ForceOpenType.FOT_CLOSE)
            case FrameState.FS_WORD_SET_NOT_EXISTS:
                self.__clear_listbox()
                self.open_close_hiding_frame(force=ForceOpenType.FOT_REFRESH)
            case FrameState.FS_WORD_SET_EXISTS | FrameState.FS_COMPLETE:
                if state == FrameState.FS_COMPLETE and GlobalData.CH_HIDE_VAR.get():
                    self.emit_word_complete(word=self.__word)
                    self.__main_frame.grid_forget()

        self.__frame_state = state

        if definition:
            self.__lbl_def.configure(text=definition)
            self.__word.set_current_definition(definition=definition)

        if highlighted:
            self.highlight()
        else:
            self.unhighlight()

        self.__lbl_word.configure(text=self.get_label_text())

        if GlobalData.current_state() == AppState.AS_BUSY:
            self.set_state(FrameState.FS_BUSY)
        elif DefinitionElement.is_complete():
            GlobalData.set_current_state(AppState.AS_CW_COMPLETE)

    def belongs_data_to_me(self, e):
        return e in [
            self.__main_frame,
            self.__hiding_frame,
            self.__lbl_word,
            self.__lbl_def,
            self.__lbl_frame,
            self.__listbox
        ]

    def highlight(self, from_mouse_move=False, event=None):
        if self.__main_frame.cget('height') > DefinitionElement.main_frame_height:
            color        = Colors.very_light_blue
            border_width = 2
        else:
            color        = Colors.very_light_grey
            border_width = 1

        if from_mouse_move is False or GlobalData.current_state() != AppState.AS_BUSY:
            self.__main_frame.configure(
                fg_color     = FrameState.get_light_color_by_state(state=self.__frame_state),
                border_color = color,
                border_width = border_width
            )
            if event:
                if event.widget.widgetName in ['canvas', 'frame', 'label', 'ttk::separator']:
                    event.widget.configure(cursor='hand2')
                else:
                    event.widget.configure(cursor='arrow')
        else:
            self.__main_frame.configure(
                cursor       = 'watch',
                border_color = Colors.black,
                border_width = 1
            )
            if event:
                event.widget.configure(cursor='watch')

    def unhighlight(self, from_mouse_move=False):
        color = Colors.very_light_blue                                                \
            if self.__main_frame.cget('height') > DefinitionElement.main_frame_height \
            else Colors.black

        if from_mouse_move is False or GlobalData.current_state() != AppState.AS_BUSY:
            self.__main_frame.configure(
                fg_color     = FrameState.get_dark_color_by_state(state=self.__frame_state),
                border_color = color,
                border_width = 1
            )
        else:
            self.__main_frame.configure(
                cursor       ='watch',
                border_color = color,
                border_width = 1
            )

    def get_label_text(self):
        return f'{self.__word.get_word()} ({self.__get_number_by_word(word=self.__word)}) '

    def open_close_hiding_frame(self, force:ForceOpenType):
        if  force != ForceOpenType.FOT_OPEN    and \
            force != ForceOpenType.FOT_REFRESH and \
            (self.__hiding_frame.winfo_manager() or
             force == ForceOpenType.FOT_CLOSE):
            if self.__hiding_frame.winfo_manager():
                self.__hiding_frame.grid_forget()
                separators = []
                all_children(frame=self.__main_frame, find_list=separators, widget_names=['ttk::separator'])
                if separators:
                    self.__main_frame.configure(
                        height       = separators[0].winfo_rooty() - self.__main_frame.winfo_rooty(),
                        border_color = Colors.very_light_grey,
                        border_width = 1
                    )
            return 'closed'
        else:
            if force != ForceOpenType.FOT_REFRESH and self.__main_frame.winfo_manager():
                self.__hiding_frame.grid(padx=0, pady=(5, 0), row=4, column=0, columnspan=2, sticky=tk.NSEW)

            self.__hiding_frame.update_idletasks()

            height = DefinitionElement.main_frame_height + self.__hiding_frame.winfo_height()
            self.__main_frame.configure(
                height       = height,
                border_color = Colors.very_light_blue,
                border_width = 2
            )
            return 'opened' if self.__main_frame.winfo_manager() else 'none'

    def add_definitions_to_listbox(self, definitions, clear, is_open=False):
        if clear:
            self.__listbox.delete(0, tk.END)
        for d in definitions:
            self.__listbox.insert(tk.END, d)
        self.__listbox.configure(height=self.__listbox.size())

        self.open_close_hiding_frame(force=ForceOpenType.FOT_REFRESH)

        if not is_open:
            if GlobalData.CH_AUTO_SEL.get():
                self.auto_select_definition()
            else:
                self.set_state(state=FrameState.FS_WORD_SET_EXISTS)
                self.unhighlight()

    def auto_select_definition(self):
        definitions = self.__listbox.get(0, tk.END)
        if definitions:
            index = random.randint(0, len(definitions) - 1)
            definition  = definitions[index]
            self.__lbl_def.configure(text=definition)
            self.__word.set_current_definition(index=index)
            self.set_state(state=FrameState.FS_COMPLETE)
            self.unhighlight()
            if GlobalData.CH_HIDE_VAR.get():
                self.__main_frame.grid_forget()

    def __clear_listbox(self):
        self.__listbox.delete(0, tk.END)
        self.__listbox.configure(height=1)
        self.__lbl_def.configure(text='')

    def __get_number_by_word(self, word):
        try:
            coord = word.get_coordinates()
            obj = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=coord[0], x=coord[1])
            return obj['text']
        except Exception as e:
            print(e)

class DefinitionElement:
    definition_elements:list[ElementData] = []
    word_definition_element_map           = {}
    row_horizontal                        = 0
    row_vertical                          = 0
    main_frame_width                      = 0
    main_frame_height                     = 60
    main_frame_pady                       = 3
    cbmode_hide                           = None
    cbmode_sel                            = None

    def create_main_frame(self, masters, word):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        master = masters[0] if word.get_direction() == Direction.HORIZONTAL else masters[1]
        row    = DefinitionElement.row_horizontal if word.get_direction() == Direction.HORIZONTAL else DefinitionElement.row_vertical

        main_frame = ctk.CTkFrame(
            master       = master,
            width        = DefinitionElement.main_frame_width,
            height       = DefinitionElement.main_frame_height,
            fg_color     = FrameState.get_dark_color_by_state(FrameState.FS_EMPTY),
            border_color = Colors.black,
            border_width = 1
        )
        main_frame.grid(row=row, column=0, padx=0, pady=DefinitionElement.main_frame_pady, sticky=tk.NSEW)
        master.grid_rowconfigure(row, weight=0)

        self.ed.set_data(key='word'        , data=word)
        self.ed.set_data(key='row'         , data=row)
        self.ed.set_data(key='main_frame'  , data=main_frame)
        self.ed.set_data(key='parent_frame', data=master)

        Highlighter(widget=main_frame)

        if word.get_direction() == Direction.HORIZONTAL:
            DefinitionElement.row_horizontal += 1
        else:
            DefinitionElement.row_vertical += 1

    def create_label_frame(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        main_frame = self.ed.get_data(key='main_frame')

        lbl_frame = ctk.CTkFrame(
            master   = main_frame,
            width    = 10,
            cursor   = 'hand2',
            bg_color = 'transparent',
            fg_color = 'transparent'
        )
        lbl_frame.grid(padx=5, pady=(2,0), row=0, column=0, sticky=tk.NSEW)

        main_frame.grid_rowconfigure   (0, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_propagate      (False)

        self.ed.set_data(key='lbl_frame', data=lbl_frame)

    def create_label_word(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        try:
            lbl_frame = self.ed.get_data(key='lbl_frame')

            lbl_word = ctk.CTkLabel(
                master        = lbl_frame,
                fg_color      = 'transparent',
                text_color    = Colors.black,
                font          = GlobalData.TITLE_FONT,
                cursor        = 'hand2',
                text          = self.ed.get_label_text(),
                anchor        = tk.W,
                corner_radius = 4
            )
            lbl_word.grid(padx=5, pady=0, row=0, column=0, sticky=tk.NSEW)
            lbl_frame.grid_rowconfigure   (0, weight=0)
            lbl_frame.grid_columnconfigure(0, weight=1)

            self.ed.set_data(key='lbl_word', data=lbl_word)
        except Exception as e:
            print(e)

    def create_selected_definition_label(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        lbl_frame = self.ed.get_data(key='lbl_frame')

        lbl_def = ttk.Label(
            master        = lbl_frame,
            background    = "#F3F6FF",
            foreground    = Colors.black,
            font          = GlobalData.VALUE_FONT,
            anchor        = tk.W,
            cursor        = 'arrow',
            text          = '',
            padding       = (5, 0, 0, 0),
            relief        = tk.GROOVE,
            borderwidth   = 1
        )
        lbl_def.grid(padx=10, pady=0, row=2, column=0, columnspan=2, sticky=tk.NSEW)
        lbl_frame.grid_rowconfigure(2, weight=0)

        self.ed.set_data(key='lbl_def', data=lbl_def)

    def create_hiding_frame(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        lbl_frame = self.ed.get_data(key='lbl_frame')
        word      = self.ed.get_data(key='word')

        hiding_frame = ctk.CTkFrame(master=lbl_frame, bg_color='transparent', fg_color='transparent')
        # Do not pack, hidden at startup
        #hiding_frame.grid(padx=0, pady=(5, 0), row=4, column=0, columnspan=2, sticky=tk.NSEW)
        lbl_frame.grid_rowconfigure(4, weight=0)

        ttk.Separator(master=hiding_frame, orient='horizontal').grid(padx=10, pady=(2,5), row=0, column=0, columnspan=2, sticky=tk.EW)
        hiding_frame.grid_rowconfigure(0, weight=0)

        listbox = tk.Listbox(
            master                       = hiding_frame,
            height                       = 1,
            background                   = Colors.very_light_grey,
            foreground                   = Colors.black,
            borderwidth                  = 1,
            selectbackground             = Colors.light_yellow,
            selectforeground             = Colors.blue,
            cursor                       = 'arrow'
        )
        listbox.grid(padx=0, pady=(0,5), row=1, column=0, sticky=tk.NSEW)

        hiding_frame.grid_rowconfigure   (1, weight=0)
        hiding_frame.grid_columnconfigure(0, weight=1)
        hiding_frame.grid_columnconfigure(1, weight=0)

        self.ed.set_data(key='listbox'     , data=listbox)
        self.ed.set_data(key='hiding_frame', data=hiding_frame)

    def bind_internal_elements(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        word           = self.ed.get_data(key='word')
        main_frame     = self.ed.get_data(key='main_frame')
        hiding_frame   = self.ed.get_data(key='hiding_frame')
        lbl_word       = self.ed.get_data(key='lbl_word')
        lbl_frame      = self.ed.get_data(key='lbl_frame')
        lbl_def        = self.ed.get_data(key='lbl_def')
        listbox        = self.ed.get_data(key='listbox')

        for w in [lbl_word, lbl_frame]:
            w.bind("<Button-1>", lambda event, word=word : (
                DefinitionElement.close_all_elements(exclude_word=word),
                DefinitionElement.open_close_hiding_frame(word=word)
            )
        )

        listbox.bind(
            '<<ListboxSelect>>',
            lambda event : self.ed.set_state(
                    state       = FrameState.FS_COMPLETE,
                    highlighted = True,
                    definition  = listbox.get(tk.ANCHOR))
                        if listbox.get(tk.ANCHOR) != ''
                        else None
        )

        widgets = [main_frame, hiding_frame, lbl_frame, lbl_word, lbl_def, listbox]
        all_children(frame=main_frame, find_list=widgets, widget_names=['ttk::separator'])

        for w in widgets:
            w.bind('<Enter>', lambda event, ed=self.ed : (
                    ed.highlight(from_mouse_move=True, event=event),
                    DefinitionElement.emit_highlighted_definition(word=word)
                )
            )
            w.bind('<Leave>', lambda event, ed=self.ed : (
                    ed.unhighlight(from_mouse_move=True),
                    DefinitionElement.emit_unhighlighted_definition(word=word)
                )
            )
        bind(self.ed, DefinitionElement.emit_word_complete, 'emit_word_complete')

    @staticmethod
    def destroy():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for de in DefinitionElement.definition_elements:
            del de

        DefinitionElement.definition_elements.clear()
        DefinitionElement.word_definition_element_map.clear()

    @staticmethod
    def get_element_by_data(source):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for ed in DefinitionElement.definition_elements:
            if ed.belongs_data_to_me(e=source):
                return ed
        return None

    @staticmethod
    def set_busy(*_):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for ed in DefinitionElement.definition_elements:
            ed.set_state(FrameState.FS_BUSY)

    @staticmethod
    def set_unbusy(*_):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for ed in DefinitionElement.definition_elements:
            ed.set_state(FrameState.FS_UNBUSY)

    @staticmethod
    def refresh():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for ed in DefinitionElement.definition_elements:
            ed.get_data('lbl_def').configure(foreground=Colors.black)
            ed.get_data('listbox').configure(foreground=Colors.black)

    @staticmethod
    def clear():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for de in DefinitionElement.definition_elements:
            de.clear()

        #DefinitionElement.definition_elements        .clear()
        #DefinitionElement.word_definition_element_map.clear()

        DefinitionElement.row_horizontal = 0
        DefinitionElement.row_vertical   = 0
        DefinitionElement.cbmode_hide    = None
        DefinitionElement.cbmode_sel     = None


    @staticmethod
    def add_element(ed:ElementData):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        DefinitionElement.definition_elements.append(ed)
        d = {ed.get_word() : ed}
        DefinitionElement.word_definition_element_map.update(d)

    @staticmethod
    def get_element(word) -> ElementData:
        #print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        return DefinitionElement.word_definition_element_map.get(word, None)

    @staticmethod
    def get_element_object(word, key):
        #print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        try:
            ed:ElementData = DefinitionElement.word_definition_element_map.get(word, None)
            if ed:
                return ed.get_data(key=key)
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def add_definitions_to_listbox(word, definitions, clear=False):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        DefinitionElement.get_element(word=word).add_definitions_to_listbox(definitions=definitions, clear=clear)

    @staticmethod
    def bind_external_elements():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        bind(CellHandler, lambda _, word, *args, **kwargs : DefinitionElement.get_element(word=word).highlight  (), 'emit_highlighted_word')
        bind(CellHandler, lambda _, word, *args, **kwargs : DefinitionElement.get_element(word=word).unhighlight(), 'emit_unhighlighted_word')

        bind(CellHandler, lambda _, word, *args, **kwargs : (
                DefinitionElement.close_all_elements(
                    parent_frame = DefinitionElement.get_element_object(word=word, key='parent_frame'),
                    exclude_word = word
                ),
                DefinitionElement.open_close_hiding_frame(word=word, **kwargs)
            ),
            'emit_open_definition'
        )

        bind(Word, lambda _, word, *args, **kwargs : (
                DefinitionElement.get_element(word=word).set_state(FrameState.FS_WORD_SET_NOT_EXISTS),
                DefinitionElement.emit_full_word_set(word=word)
            ),
            'emit_full_word_set'
        )
        bind(
            Word,
            lambda _, word, *args, **kwargs :
                DefinitionElement.get_element(word=word).set_state(FrameState.FS_EMPTY),
            'emit_word_emptied'
        )
        if DefinitionElement.cbmode_hide:
            GlobalData.CH_HIDE_VAR.trace_remove('write', DefinitionElement.cbmode_hide)
        if DefinitionElement.cbmode_sel:
            GlobalData.CH_AUTO_SEL.trace_remove('write', DefinitionElement.cbmode_sel)
        DefinitionElement.cbmode_hide = GlobalData.CH_HIDE_VAR.trace_add('write', DefinitionElement.show_all_definitions)
        DefinitionElement.cbmode_sel  = GlobalData.CH_AUTO_SEL.trace_add('write', DefinitionElement.auto_select_definitions)

    @staticmethod
    def open_close_hiding_frame(word:Word, force:ForceOpenType=ForceOpenType.FOT_NONE, sender=None):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        action = DefinitionElement.get_element(word=word).open_close_hiding_frame(force=force)
        if action != 'none':
            DefinitionElement.emit_open_definition(
                parent_frame = DefinitionElement.get_element_object(word=word, key='parent_frame'),
                frame        = DefinitionElement.get_element_object(word=word, key='main_frame'),
                ed           = DefinitionElement.get_element(word=word) if action == 'opened' else None,
                sender       = sender
            )

    @staticmethod
    def close_all_elements(parent_frame=None, exclude_word=None):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        exclude_this = DefinitionElement.get_element(word=exclude_word) if exclude_word else None
        for w_map in DefinitionElement.word_definition_element_map.items():
            if w_map[1] != exclude_this and (parent_frame is None or w_map[1].get_parent() == parent_frame):
                w_map[1].open_close_hiding_frame(force=ForceOpenType.FOT_CLOSE)

    @staticmethod
    def update_size():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        parent_frames_done = []
        for w_map in DefinitionElement.word_definition_element_map.items():
            parent_frame = DefinitionElement.get_element_object(word=w_map[0], key='parent_frame')
            main_frame   = DefinitionElement.get_element_object(word=w_map[0], key='main_frame')
            width        = int(get_parent_widget(widget=parent_frame, level=4).winfo_width() / 2) - 50
            main_frame.configure(height=DefinitionElement.main_frame_height, width=width)

            if parent_frame not in parent_frames_done:
                parent_frames_done.append(parent_frame)
                parent_frame.update() # update the scrollbar

    @staticmethod
    def update_frame_without_definitions(word, word_exists):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        de = DefinitionElement.get_element(word=word)
        de.set_state(FrameState.FS_EMPTY if word.is_empty() else FrameState.FS_WORD_SET_EXISTS if word_exists else FrameState.FS_WORD_SET_NOT_EXISTS)
        de.unhighlight()

    @staticmethod
    def show_all_definitions(*_):
        with AppThreadExecutor(
                method       = DefinitionElement.__show_all_definitions,
                result_state = AppState.AS_CW_FILLED,
                message_key  = 'auto_hide_def' if GlobalData.CH_HIDE_VAR.get() else 'auto_show_def',
                show_cancel  = False
            ): pass

    @staticmethod
    def __show_all_definitions():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if GlobalData.BLOCK_SIGNALS:
            return

        parent_frames_done = []

        for ed in DefinitionElement.definition_elements:
            pf = ed.get_data(key='parent_frame')
            if not pf in parent_frames_done:
                parent_frames_done.append(pf)
                canvas = pf.canvas()
                canvas.yview_moveto(0.0)

            main_frame = ed.get_data(key='main_frame')
            if GlobalData.CH_HIDE_VAR.get():
                lbl_def = ed.get_data(key='lbl_def')
                if lbl_def.cget('text'):
                    DefinitionElement.open_close_hiding_frame(
                        word  = ed.get_data(key='word'),
                        force = ForceOpenType.FOT_CLOSE
                    )
                    main_frame.grid_forget()
                    DefinitionElement.emit_definition_closed()
            else:
                row = ed.get_data(key='row')
                main_frame.grid(row=row, column=0, padx=0, pady=DefinitionElement.main_frame_pady, sticky=tk.NSEW)
                main_frame.grid_propagate(False)
        DefinitionElement.update_size()

    @staticmethod
    def auto_select_definitions(*_):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        if GlobalData.BLOCK_SIGNALS:
            return

        if GlobalData.CH_AUTO_SEL.get():
            with AppThreadExecutor(
                method       = DefinitionElement.__auto_select_definitions,
                result_state = AppState.AS_CW_FILLED,
                message_key  = 'auto_sel_def',
                show_cancel  = False
            ): pass

            if DefinitionElement.is_complete():
                GlobalData.set_current_state(AppState.AS_CW_COMPLETE)

    @staticmethod
    def __auto_select_definitions():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for w_map in DefinitionElement.word_definition_element_map.items():
            print(f'Auto selecting definition for word {w_map[0].get_word()}')
            DefinitionElement.get_element(word=w_map[0]).auto_select_definition()

    @staticmethod
    def is_complete():
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        for de in DefinitionElement.definition_elements:
            if de.get_data('frame_state') != FrameState.FS_COMPLETE:
                return False
        return True


    def __init__(self, masters, word, is_open):
        self.masters   = masters
        self.word:Word = word
        self.is_open   = is_open

        self.ed = ElementData()

        print(f'creating elements for word {self.word.get_word()}')

    def __enter__(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        try:
            self.create_main_frame               (masters=self.masters, word=self.word)
            self.create_label_frame              ()
            self.create_hiding_frame             ()
            self.create_label_word               ()
            self.create_selected_definition_label()
        except Exception as e:
            print(e)

    def __exit__(self, *_):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        DefinitionElement.add_element(ed=self.ed)
        self.bind_internal_elements()

        if self.is_open:
            self.__update_element()

    def __update_element(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.ed.add_definitions_to_listbox(definitions=self.word.get_definitions(), clear=True, is_open=True)
        definition = self.word.get_current_definition()
        if definition:
            self.ed.set_state(state=FrameState.FS_COMPLETE, highlighted=False, definition=definition)
        else:
            self.ed.set_state(state=FrameState.FS_WORD_SET_EXISTS, highlighted=False)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    set_style()

    GlobalData.main_window.geometry('800x400')

    for ii in range(10):
        GlobalData.words.append(Word(
                coordinates = (ii, 0),
                length      = 5,
                word        = f'TEST{ii}',
                direction   = Direction.HORIZONTAL
            ))
        CwcMatrix.set(matrix_type=MatrixType.VARIABLE, y=ii, x=0, value=tk.StringVar())
        CwcMatrix.set(matrix_type=MatrixType.NUMBER  , y=ii, x=0, value=tk.Label())

        GlobalData.words.append(Word(
                coordinates = (0, ii),
                length      = 5,
                word        = f'TEST{ii}',
                direction   = Direction.VERTICAL
            ))
        CwcMatrix.set(matrix_type=MatrixType.VARIABLE, y=0, x=ii, value=tk.StringVar())
        CwcMatrix.set(matrix_type=MatrixType.NUMBER  , y=0, x=ii, value=tk.Label())

    f = GlobalData.main_tkmt_window.addLabelFrame(' Definizioni ', sticky=tk.NSEW, padx=5, pady=5, row=0, col=0)
    GlobalData.main_tkmt_window.root.grid_rowconfigure   (0, weight=1)
    GlobalData.main_tkmt_window.root.grid_columnconfigure(0, weight=1)
    GlobalData.main_tkmt_window.root.grid_columnconfigure(1, weight=1)

    frame_left = ctk.CTkScrollableFrame(
        master                       = GlobalData.main_window,
        orientation                  = 'both',
        border_color                 = Colors.light_grey,
        scrollbar_button_hover_color = Colors.orange,
        border_width                 = 1
    )
    frame_left.grid(padx=5, pady=0, row=0, column=0, sticky=tk.NSEW)

    frame_right = ctk.CTkScrollableFrame(
        master                       = GlobalData.main_window,
        orientation                  = 'both',
        border_color                 = Colors.light_grey,
        scrollbar_button_hover_color = Colors.orange,
        border_width                 = 1
    )
    frame_right.grid(padx=5, pady=0, row=0, column=1, sticky=tk.NSEW)

    bind(DefinitionElement, lambda : print('emit_word_complete'), 'emit_word_complete')

    for _word in GlobalData.words:
        with DefinitionElement(
            masters = (frame_left, frame_right),
            word    = _word,
            is_open = False
        ): pass

    bind(DefinitionElement, lambda *args, **kargs: print('emit_highlighted_definition'  ), 'emit_highlighted_definition')
    bind(DefinitionElement, lambda *args, **kargs: print('emit_unhighlighted_definition'), 'emit_unhighlighted_definition')
    bind(DefinitionElement, lambda *args, **kargs: print('emit_open_definition'         ), 'emit_open_definition')

    DefinitionElement.update_size()

    GlobalData.CH_HIDE_VAR.set(False)
    #GlobalData.main_window.after(500, lambda : Word.emit_full_word_set(word=GlobalData.words[0]))
    GlobalData.main_tkmt_window.root.mainloop()
