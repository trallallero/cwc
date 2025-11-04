""" Base class for a cell in the crossword grid. """

import pyautogui

from cwc_globals import (
    Direction,
    GlobalData,
    AppState,
    bind
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)

from highlighter import Highlighter

class CellBase:
    """ Base class for a cell in the crossword grid. 
    TODO: document it
    """

    def __init__(self, y, x, widget):
        self.__y                       = y
        self.__x                       = x
        self.__widget                  = widget
        self.__words                   = []
        self.__hl:Highlighter          = None
        self.__current_bind_dbl_click  = None
        self.__method_vert             = None
        self.__method_horiz            = None
        self.__last_mouse_point_status = Direction.NONE

    def get_direction(self):
        return Direction.NONE

    def bind_events(self):
        self.__widget.bind("<Button-1>"  , self.__left_click)
        self.__widget.bind("<KeyRelease>", self.__key_release)

        if CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=self.__y, x=self.__x):
            self.__widget.bind("<Button-3>", self.__right_click)

        if self.__hl:
            bind(self.__hl, self.__highlighted_word  , 'emit_highlighted_word')
            bind(self.__hl, self.__unhighlighted_word, 'emit_unhighlighted_word')

        self.__widget.bind("<Enter>"   , self.__mouse_enter)
        self.__widget.bind("<Leave>"   , self.__mouse_leave)

        if self.__widget.widgetName == 'ttk::entry':
            if len(self.words()) == 1:
                self.__widget.bind('<Double-Button-1>', lambda _: self.__double_click(sender=self.__widget, word=self.words()[0]))

            if len(self.words()) == 2: # this will bind on mouse move
                self.__method_vert  = lambda _: self.__double_click(sender=self.__widget, word=self.words()[Direction.VERTICAL.value])
                self.__method_horiz = lambda _: self.__double_click(sender=self.__widget, word=self.words()[Direction.HORIZONTAL.value])

    def add_word(self, w):
        self.__words.append(w)
        if len(self.words()) == 2:
            if self.words()[Direction.VERTICAL.value].get_direction() != Direction.VERTICAL:
                self.__words[Direction.VERTICAL.value], self.__words[Direction.HORIZONTAL.value] = \
                    self.__words[Direction.HORIZONTAL.value], self.__words[Direction.VERTICAL.value]

    def words(self):
        return self.__words

    def y(self):
        return self.__y

    def x(self):
        return self.__x

    def set_highlighter(self):
        self.__hl = Highlighter(widget=self)

    def get_highlighter(self):
        return self.__hl

    def del_highlighter(self):
        if self.__hl:
            del self.__hl
            self.__hl = None

    def is_empty(self):
        for w in self.words():
            if not '_' in w.get_word():
                return False
        return True

    def set_word(self, letters:str):
        lenght = len(self.words())
        if lenght == 1 or (lenght == 2 and self.__get_highlighted_word_index() >= 0):
            w = self.__words[0] if lenght == 1 else self.__words[self.__get_highlighted_word_index()]
            w.set_word(letters=letters.ljust(w.get_length(), '_'))

    def clear(self):
        self.__words.clear()
        self.del_highlighter()

    def highlight_word(self, word=None):
        if self.get_highlighter():
            self.get_highlighter().highlight_word(word=word if word else self.get_word(text=False))

    def unhighlight_word(self):
        if self.get_highlighter():
            self.get_highlighter().unhighlight_word()

    def get_word(self, text=True):
        last_highlighted_word_index = self.__get_last_highlighted_word_index()

        if last_highlighted_word_index >= 0 and len(self.words()) > last_highlighted_word_index:
            w = self.words()[last_highlighted_word_index]
            return w.get_word() if text else w

        if len(self.words()) >= 1:
            return self.words()[0].get_word() if text else self.words()[0]

        return None

    def get_text(self):
        return self['text']

    def __highlighted_word(self, word):
        self.emit_highlighted_word(word=word)

    def __unhighlighted_word(self, word):
        self.emit_unhighlighted_word(word=word)

    def __mouse_enter(self, *_):
        if GlobalData.current_state() == AppState.AS_BUSY:
            self.__widget.configure(cursor='watch')
            return

        if self.__widget.widgetName == 'ttk::label':
            self.__widget.configure(cursor='hand2')

        if len(self.words()) == 1:
            self.emit_cell_entered(sender=self, word=self.words()[0])
        elif len(self.words()) == 2:
            mouse_point     = int(pyautogui.position()[0])
            half_cell_point = int(self.__widget.winfo_rootx() + (self.__widget.winfo_width() / 2))

            if mouse_point <= half_cell_point:
                self.emit_cell_entered(sender=self, word=self.words()[Direction.HORIZONTAL.value])
            else:
                self.emit_cell_entered(sender=self, word=self.words()[Direction.VERTICAL.value])

            self.bind("<Motion>", self.__on_mouse_move)

    def __mouse_leave(self, *_):
        if GlobalData.current_state() == AppState.AS_BUSY:
            return

        if len(self.words()) == 2:
            self.unbind("<Motion>")
        self.emit_cell_exited(sender=self)

    def __on_mouse_move(self, _=None):
        mouse_point = int(pyautogui.position()[0])
        direction   = None

        half_cell_point = int(self.__widget.winfo_rootx() + (self.__widget.winfo_width() / 2))
        if mouse_point <= half_cell_point and (self.__current_bind_dbl_click != self.__method_horiz or self.__widget.widgetName != 'ttk::entry'):
            direction = Direction.HORIZONTAL
        elif mouse_point > half_cell_point and (self.__current_bind_dbl_click != self.__method_vert or self.__widget.widgetName != 'ttk::entry'):
            direction = Direction.VERTICAL

        if self.__last_mouse_point_status == direction:
            return
        self.__last_mouse_point_status = direction

        if direction:
            #print(f'binding to {direction}')
            self.__widget.unbind('<Double-Button-1>')
            if direction == Direction.VERTICAL:
                if self.__widget.widgetName == 'ttk::entry':
                    self.__widget.bind('<Double-Button-1>', self.__method_vert)
                    self.__current_bind_dbl_click = self.__method_vert
                self.unhighlight_word()
                self.highlight_word(word=self.words()[Direction.VERTICAL.value])
            else:
                if self.__widget.widgetName == 'ttk::entry':
                    self.__widget.bind('<Double-Button-1>', self.__method_horiz)
                    self.__current_bind_dbl_click = self.__method_horiz
                self.unhighlight_word()
                self.highlight_word(word=self.words()[Direction.HORIZONTAL.value])

    def __double_click(self, sender=None, word=None):
        self.emit_double_click(sender=sender, word=word)

    def __left_click(self, *_):
        if CwcMatrix.get(
            matrix_type = MatrixType.BOOLEAN,
            y           = self.__y,
            x           = self.__x) and len(self.words()) < 2:
            self.emit_left_click(sender=self, word=self.words()[0] if self.words() else None)
        else:
            mouse_point     = int(pyautogui.position()[0])
            half_cell_point = int(self.__widget.winfo_rootx() + (self.__widget.winfo_width() / 2))

            if mouse_point <= half_cell_point:
                self.emit_left_click(sender=self, word=self.words()[Direction.HORIZONTAL.value])
            else:
                self.emit_left_click(sender=self, word=self.words()[Direction.VERTICAL.value])

    def __right_click(self, event=None):
        if event.widget.widgetName == 'ttk::entry':
            self.emit_show_popup(event=event)

    def __key_release(self, event=None):
        if event.widget.widgetName == 'ttk::entry' or \
           (event.widget.widgetName == 'ttk::label' and event.keysym == 'Tab'):
            self.emit_key_released(event=event)
            return "break"

    def __get_last_highlighted_word_index(self):
        return self.get_highlighter().get_last_highlighted_word_index() if self.get_highlighter() else -1

    def __get_highlighted_word_index(self):
        return self.get_highlighter().get_highlighted_word_index() if self.get_highlighter() \
            else -1


############# TESTS #############

if __name__ == "__main__":
    from word import Word

    cb = CellBase(y=0, x=0, widget=GlobalData.main_window)

    assert cb.get_direction() == Direction.NONE

    cb.add_word(w=Word(
            coordinates = (0, 0),
            length      = 4,
            word        = 'TEST',
            direction   = Direction.VERTICAL
        )
    )
    assert cb.get_direction  ()   == Direction.NONE # base class, no direction info
    assert cb.get_highlighter()   is None
    cb.set_highlighter()
    assert cb.get_highlighter()   is not None
    assert cb.get_word(text=True) == 'TEST'
