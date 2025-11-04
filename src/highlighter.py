"""Module to highlight a word"""

from cwc_globals import (
    GlobalData,
    Colors,
    AppState,
    Direction,
    get_parent_widget,
    bind
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)

class Highlighter:
    """Class to highlight a word"""

    def __init__(self, widget):
        self.widget                        = widget
        self.__highlighted_word_index      = Direction.NONE
        self.__last_highlighted_word_index = Direction.NONE

    def get_highlighted_word_index(self):
        return self.__highlighted_word_index.value

    def get_last_highlighted_word_index(self):
        return self.__last_highlighted_word_index.value

    def highlight_word(self, word):
        if GlobalData.current_state() == AppState.AS_BUSY:
            self.widget.configure(cursor='watch')
            return

        self.__highlight_word_internal(word=word)
        if word:
            self.emit_highlighted_word(word=word)

    def unhighlight_word(self):
        if GlobalData.current_state() == AppState.AS_BUSY:
            return

        words = self.__highlight_word_internal(highlight=False)
        self.__highlighted_word_index = Direction.NONE
        for word in words:
            self.emit_unhighlighted_word(word=word)

    def __highlight_word_internal(self, word=None, highlight=True):
        words = [word] if word else self.widget.words()

        for w in words:
            if self.widget.widgetName == 'ttk::entry':
                self.widget.configure(cursor='sb_h_double_arrow' if w.get_direction() == Direction.HORIZONTAL else 'sb_v_double_arrow')

            if highlight:
                self.__last_highlighted_word_index = w.get_direction()

            coord = w.get_coordinates()
            y     = coord[0]
            x     = coord[1]

            while CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x):
                num_lbl = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=y, x=x)
                entry   = CwcMatrix.get(matrix_type=MatrixType.ENTRY , y=y, x=x)
                frame   = get_parent_widget(widget=entry)

                if highlight:
                    entry['style'] = 'Highlight.Label'
                    frame['style'] = 'Highlight.Label'
                    if num_lbl:
                        num_lbl.highlight()
                else:
                    frame['style'] = 'White.Label'
                    entry['style'] = 'White.Label'
                    if num_lbl:
                        num_lbl.unhighlight()

                if w.get_direction() == Direction.HORIZONTAL:
                    x +=1
                else:
                    y +=1
                if x >= GlobalData.TOT_COLS or y >= GlobalData.TOT_ROWS:
                    break
        return words


############# TESTS #############

if __name__ == "__main__":
    import tkinter as tk
    from cwc_style  import set_style
    import customtkinter as ctk
    from definition_element import DefinitionElement, FrameState
    from crossword import Crossword
    from TKinterModernThemes.WidgetFrame import WidgetFrame
    from word import Word
    from cell_handler import CellHandler

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
