"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to handle cell interactions in the crossword grid. """

import pyautogui

from cwc_globals import (
    GlobalData,
    Colors,
    Direction,
    bind,
    get_parent_widget,
    get_empty_words_coordinates
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)
from word import (
    Word,
    clear_word,
    set_char_to_words,
    del_char_from_words,
    get_cell_by_word,
    get_word_by_coord_and_direction,
    del_chars_not_used_by_other_words
)
from crossword_filler import (
    CrosswordFiller,
    ExcludedWhen
)

from input_panel  import InputPanel
from cell_entry   import CellEntry
from popup_menu   import PopupMenu
from translations import gtbk
from word_editor  import WordEditor


class CellHandler:
    """ Class to handle cell interactions in the crossword grid.
    TODO: document it
    """

    def __init__(self):
        self.selected_cell:CellEntry    = None
        self.current_automove_direction = None
        self.start_new_word             = None

    def bind_events(self):
        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                if CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x):
                    cell = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=y, x=x)
                    cell.bind_events()
                    self.bind_cell_events(cell=cell)
                    num_lbl = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=y, x=x)
                    if num_lbl:
                        num_lbl.bind_events()
                        self.bind_cell_events(cell=num_lbl)

    def bind_cell_events(self, cell:CellEntry):
        bind(cell, self.cell_entered        , 'emit_cell_entered')
        bind(cell, self.cell_exited         , 'emit_cell_exited')
        bind(cell, self.cell_double_clicked , 'emit_double_click')
        bind(cell, self.cell_left_clicked   , 'emit_left_click')
        bind(cell, self.cell_menu_popup     , 'emit_show_popup')
        bind(cell, self.cell_key_released   , 'emit_key_released')
        bind(cell, self.__highlighted_word  , 'emit_highlighted_word')
        bind(cell, self.__unhighlighted_word, 'emit_unhighlighted_word')

    def __highlighted_word(self, word):
        CellHandler.emit_highlighted_word(word)

    def __unhighlighted_word(self, word):
        CellHandler.emit_unhighlighted_word(word=word)

    def cell_entered(self, sender:CellEntry, word):
        if sender:
            sender.highlight_word(word=word)

    def cell_exited(self, sender:CellEntry):
        if sender:
            if sender == self.selected_cell:
                self.__deselect_cell(self.selected_cell)
            sender.unhighlight_word()

    def cell_double_clicked(self, sender:CellEntry=None, word=None):
        self.__deselect_cell(cell=sender)
        self.find_word(word=word)

    def cell_left_clicked(self, sender:CellEntry, word):
        if sender.widgetName == 'ttk::label' and len(sender.words()) > 0:
            self.emit_open_definition(word=word, sender=sender)
        elif sender.widgetName == 'ttk::entry':
            if word and get_word_by_coord_and_direction(coord=(sender.y(), sender.x()), direction=word.get_direction()):
                self.start_new_word = (sender.y(), sender.x(), word)
            else:
                self.start_new_word = None
            self.set_selected(cell=sender, focus=True, from_mouse_click=True)

    def highlight_word(self, word):
        cell = get_cell_by_word(word=word)
        if cell:
            cell.highlight_word(word=word)

    def unhighlight_word(self, word):
        cell = get_cell_by_word(word=word)
        if cell:
            cell.unhighlight_word()

    def cell_menu_popup(self, event=None):
        pm = PopupMenu(master=event.widget)
        bind(pm, self.menu_method, 'menu_method')
        pm.show()

    def menu_method(self, key, widget):
        match key:
            case 'find_word':
                self.find_word(word=widget.get_word(text=False))
                return
            case 'del_word':
                clear_word(word=widget.get_word(text=False))
                return
            case 'del_find_word':
                clear_word(word=widget.get_word(text=False))
                self.find_word(word=widget.get_word(text=False))
                return
            case 'del_exclude_word_once':
                CrosswordFiller.exclude_word(
                    word = widget.get_word(),
                    when = ExcludedWhen.EW_ONCE
                )
                clear_word(word=widget.get_word(text=False))
            case 'del_exclude_word_session':
                CrosswordFiller.exclude_word(
                    word = widget.get_word(),
                    when = ExcludedWhen.EW_SESSION
                )
                clear_word(word=widget.get_word(text=False))
            case 'del_exclude_word_always':
                CrosswordFiller.exclude_word(
                    word = widget.get_word(),
                    when = ExcludedWhen.EW_ALWAYS
                )
                clear_word(word=widget.get_word(text=False))
            case 'del_other_words':
                bk_word = widget.get_word(text=False)
                for w in GlobalData.words:
                    widget.clear()
                    clear_word(word=w)
                widget.add_word(w=bk_word)
            case 'del_not_used_keys':
                del_chars_not_used_by_other_words(word=widget.get_word(text=False))
                return
            case 'del_find_not_used_keys':
                del_chars_not_used_by_other_words(word=widget.get_word(text=False))
                self.find_word(word=widget.get_word(text=False))
                return
            case 'del_char':
                del_char_from_words(y=widget.y(), x=widget.x())
                return
            case 'handle_word':
                WordEditor(word=widget.get_word(text=False))
                return

    def set_selected(self, cell:CellEntry, focus=True, from_mouse_click=False, direction=None):
        try:
            if len(cell.words()) == 2: # cell already selected, might select the other word
                if direction is None:
                    mouse_point     = int(pyautogui.position()[0])
                    half_cell_point = int(cell.winfo_rootx() + (cell.winfo_width() / 2))
                    if mouse_point <= half_cell_point:
                        direction = Direction.HORIZONTAL
                    elif mouse_point > half_cell_point: # horizontal
                        direction = Direction.VERTICAL

                if direction == Direction.VERTICAL:
                    if self.selected_cell == cell and self.current_automove_direction == Direction.VERTICAL:
                        self.__deselect_cell(cell=cell)
                        cell.highlight_word()
                    else:
                        self.select_cell(cell=cell, direction=Direction.VERTICAL, from_mouse_click=from_mouse_click)
                        if focus:
                            cell.focus_set()
                elif direction == Direction.HORIZONTAL:
                    if self.selected_cell == cell and self.current_automove_direction == Direction.HORIZONTAL:
                        self.__deselect_cell(cell=cell)
                        cell.highlight_word()
                    else:
                        self.select_cell(cell=cell, direction=Direction.HORIZONTAL, from_mouse_click=from_mouse_click)
                        if focus:
                            cell.focus_set()
            elif self.selected_cell != cell:
                if direction is None:
                    direction = cell.get_direction()
                if from_mouse_click:
                    self.current_automove_direction = direction
                self.select_cell(
                    cell             = cell,
                    direction        = direction,
                    from_mouse_click = from_mouse_click
                )
                if focus:
                    cell.focus_set()
            else:
                self.__deselect_cell(cell=cell)
                cell.highlight_word()
        except Exception as e:
            print(e)

    def select_cell(self, cell:CellEntry, direction, from_mouse_click):
        if self.selected_cell:
            self.__deselect_cell(cell=self.selected_cell)

        parent_widget = get_parent_widget(widget=cell)
        if not parent_widget:
            return

        children = parent_widget.winfo_children()
        labels   = [c for c in children if c.widgetName == 'ttk::label']
        label    = labels[0] if labels else None

        cell         ['style'] = 'Orange.Label'
        parent_widget['style'] = 'Orange.Label'
        if label:
            label.select()

        self.selected_cell = cell
        self.set_direction_to_label(cell=cell, direction=direction, from_mouse_click=from_mouse_click)

    def deselect_cells(self):
        self.__deselect_cell(self.selected_cell)

    def __deselect_cell(self, cell:CellEntry):
        if not cell:
            return

        parent_widget = get_parent_widget(widget=cell)

        if not parent_widget:
            return

        children = parent_widget.winfo_children()
        labels   = [c for c in children if c.widgetName == 'ttk::label']
        label    = labels[0] if labels else None

        if CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=cell.y(), x=cell.x()):
            cell         ['style'] = 'White.TFrame'
            parent_widget['style'] = 'White.Label'
            if label:
                label.unhighlight()
        else:
            cell         ['style'] = 'Black.TFrame'
            parent_widget['style'] = 'Black.TFrame'
        cell.configure(state='disabled')
        cell.focus_get()
        self.set_direction_to_label(cell=cell, direction=None)
        self.selected_cell = None

    def set_direction_to_label(self, cell:CellEntry, direction, from_mouse_click=False):
        num_lbl = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=cell.y(), x=cell.x())
        if not num_lbl:
            return

        text = str(num_lbl['text']).replace(GlobalData.VERT_ARROW, '').replace(GlobalData.HORIZ_ARROW, '').strip()

        if from_mouse_click:
            if direction == Direction.VERTICAL:
                text += '  ' + GlobalData.VERT_ARROW
                self.current_automove_direction = Direction.VERTICAL
            elif direction == Direction.HORIZONTAL:
                text += '  ' + GlobalData.HORIZ_ARROW
                self.current_automove_direction = Direction.HORIZONTAL
            else:
                self.current_automove_direction = None

        num_lbl.configure(text=text)

    def cell_key_released(self, event=None, data=None):
        if not self.selected_cell:
            return

        if event:
            char   = str(event.keysym).lower()
            widget = event.widget
            y      = widget.y()
            x      = widget.x()
        elif data:
            char   = data['char']
            widget = data['widget']
            y      = data['y']
            x      = data['x']
        else:
            return

        if  char == 'space':
            return
        elif char == 'tab':
            if self.selected_cell:
                self.__handle_selection_move(char=char, y=self.selected_cell.y(), x=self.selected_cell.x())
        elif char == 'escape':
            pass
        elif char == 'delete':
            del_char_from_words(y=y, x=x)
        elif char.isalpha() and len(char) == 1:
            set_char_to_words(y=y, x=x, char=char.upper())
            if GlobalData.AUTO_MOVE.get():
                self.__deselect_cell(cell=widget)
                self.__handle_selection_move(char=self.get_auto_move_key_by_current_direction(), y=y, x=x)
        elif char in ['up', 'down', 'left', 'right']:
            self.__handle_selection_move(char=char, y=y, x=x)
        else:
            return
        GlobalData.main_window.update()

    def __handle_selection_move(self, char, y, x):
        if (GlobalData.SKIP_BLACK_CELLS.get() and
            CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x) == 0) or \
           (char == 'tab' and self.start_new_word)                                      or \
           char == 'up'    and y <= 0                                                   or \
           char == 'down'  and y >= (GlobalData.TOT_ROWS - 1)                           or \
           char == 'left'  and x <= 0                                                   or \
           char == 'right' and x >= (GlobalData.TOT_COLS - 1):
            w = self.__get_next_word(y=y, x=x)
            if w:
                self.start_new_word = (w.get_y(), w.get_x(), w)
                if self.selected_cell:
                    self.selected_cell.unhighlight_word()
                cell:CellEntry = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=w.get_y(), x=w.get_x())
                cell.highlight_word(word=w)
                self.set_selected(cell=cell, focus=True, from_mouse_click=True, direction=w.get_direction())
                if cell.get_text() != '':
                    self.cell_key_released(data={'char' : cell.get_text().lower(), 'widget' : cell, 'y' : w.get_y(), 'x' : w.get_x()})
            return
        if char == 'up':
            y -= 1
        elif char == 'down':
            y += 1
        elif char == 'left':
            x -= 1
        elif char == 'right':
            x += 1

        try:
            if GlobalData.SKIP_BLACK_CELLS.get() and CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x) == 0:
                self.__handle_selection_move(char=char, y=y, x=x)
            else:
                self.set_selected(cell=CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=y, x=x), focus=True)
        except Exception as e:
            print(e)

    def get_auto_move_key_by_current_direction(self):
        return 'right' if self.current_automove_direction == Direction.HORIZONTAL else \
               'down'  if self.current_automove_direction == Direction.VERTICAL   else \
                None

    def __get_next_word(self, y, x):
        if self.start_new_word:
            y    = self.start_new_word[0]
            x    = self.start_new_word[1]
            word = self.start_new_word[2]
            self.start_new_word = None
        else:
            word = None

        w_coords = get_empty_words_coordinates()

        for item in w_coords:
            coord = item['c']
            if coord[1] != x or coord[0] != y or item['w'] != word:
                return item['w']
        return None

    def find_word(self, word):
        print(f'getting words for {word.get_name()} - like {word.get_word()}')
        value = InputPanel(title=gtbk('choose_word')).get_word(like=word.get_word()).upper()
        if value != '':
            word.set_word(letters=value)


############# TESTS #############

if __name__ == "__main__":
    import tkinter as tk
    from cwc_style  import set_style
    import customtkinter as ctk
    from definition_element import DefinitionElement, FrameState
    from crossword import Crossword
    from TKinterModernThemes.WidgetFrame import WidgetFrame

    set_style()

    main_frame = ctk.CTkFrame(
        master       = GlobalData.main_window,
        width        = DefinitionElement.main_frame_width,
        height       = DefinitionElement.main_frame_height,
        fg_color     = FrameState.get_dark_color_by_state(FrameState.FS_EMPTY),
        border_color = Colors.grey,
        border_width = 1
    )
    main_frame.grid(row=0, column=0, padx=0, pady=DefinitionElement.main_frame_pady, sticky=tk.NSEW)

    GlobalData.main_window.grid_rowconfigure   (0, weight=1)
    GlobalData.main_window.grid_columnconfigure(0, weight=1)

    GlobalData.TOT_ROWS = 1
    GlobalData.TOT_COLS = 4

    for i in range(4):
        CwcMatrix.set(matrix_type=MatrixType.BOOLEAN, y=0 , x=i, value=True)
        CwcMatrix.set(matrix_type=MatrixType.VARIABLE, y=0, x=i, value=tk.StringVar())

    GlobalData.words.append(
        Word(
            coordinates = (0, 0),
            length      = 4,
            word        = 'TEST',
            direction   = Direction.HORIZONTAL
        )
    )

    bind(Crossword, lambda *args, **kargs : print('emit_finalize_crossword'), 'emit_finalize_crossword')

    wf = WidgetFrame(master=main_frame, name='')

    Crossword.create_crossword(master=wf, is_open=True)
    Crossword.finalize_crossword()

    bind(CellHandler, lambda *args, **kargs: print('emit_highlighted_word')  , 'emit_highlighted_word')
    bind(CellHandler, lambda *args, **kargs: print('emit_unhighlighted_word'), 'emit_unhighlighted_word')
    CellHandler().bind_events()


    GlobalData.main_window.mainloop()
