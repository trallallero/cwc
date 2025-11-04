"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module defining the Crossword class to create and manage the crossword grid and words. """

import operator

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals import (
    Theme,
    GlobalData,
    Direction,
    Colors,
    clear_words,
    clear_all,
    get_matrix_dimensions,
    bind
)

from cwc_matrix import (
    CwcMatrix,
    MatrixType
)

from word import (
    Word,
    get_word_by_coord_and_direction
)

from black_cell_handler import BlackCellHandler
from cell_entry         import CellEntry
from cwc_button         import CwcButtonTkmt
from cell_label         import CellLabel
from translations       import gtbk

class Crossword:
    """ Class defining the Crossword class to create and manage the crossword grid and related
    words. Calls an not implemented "Crossword.emit_finalize_crossword" method that needs to be
    bound by the caller class.
    """

    __master_frame   :WidgetFrame            = None
    __frame_cwc      :ttk.Frame              = None
    __inner_frame_cwc:ttk.Frame              = None
    __scroll_frame   :ctk.CTkScrollableFrame = None
    __btn_frame:WidgetFrame                  = None
    __btn_finalize:CwcButtonTkmt             = None
    __objects_map                            = []
    __invalid_cells                          = []
    __black_cells                            = []
    __black_frames                           = []

    @staticmethod
    def create_crossword(master:WidgetFrame, is_open=False):
        """Creates the crossword using BlackCellHandler to determine if creating a black
        or white cell, if IS_OPEN is False. After having created and IS_OPEN is False,
        calls again BlackCellHandler to correct the isolated white cells
        (means a single useless white cell surrounded by black cells and/or margins).
        If IS_OPEN is True, creates the crossword using cwc_matrices BOOLEAN
        """

        Crossword.__master_frame = master

        Crossword.__invalid_cells.clear()
        Crossword.__black_cells  .clear()
        Crossword.__black_frames .clear()
        Crossword.__objects_map  .clear()

        if is_open is False:
            clear_all()
            CwcMatrix.clear_matrices()

        Crossword.__scroll_frame = ctk.CTkScrollableFrame(
            master                       = master.master,
            orientation                  = 'both',
            fg_color                     = str(Colors.label_frame_col),
            bg_color                     ='transparent',
            scrollbar_button_color       = Colors.very_light_grey
                if Theme.CURRENT_APP_MODE == 'light'
                else Colors.grey,
            border_color                 = Colors.light_grey,
            scrollbar_button_hover_color = Colors.orange,
            border_width                 = 1
        )

        Crossword.__create_finalize_btn_frame(master=Crossword.__scroll_frame)

        Crossword.__frame_cwc = ttk.Frame(
            master      = Crossword.__scroll_frame,
            relief      = tk.RAISED,
            borderwidth = 3,
            style       = 'Custom.TFrame'
        )
        Crossword.__frame_cwc.grid(row=1, column=0, padx=10, pady=10)

        Crossword.__inner_frame_cwc = ttk.Frame(
            master      = Crossword.__frame_cwc,
            relief      = tk.FLAT,
            borderwidth = 0,
            style       = 'Black.TFrame'
        )
        Crossword.__inner_frame_cwc.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=1, pady=1)
        Crossword.__inner_frame_cwc.pack_propagate(False)

        try:
            for y in range(GlobalData.TOT_ROWS):
                for x in range(GlobalData.TOT_COLS):
                    frame = ttk.Frame(
                        master      = Crossword.__inner_frame_cwc,
                        relief      = tk.SOLID,
                        borderwidth = 0,
                        width       = 48,
                        height      = 48,
                        style       = 'White.TFrame'
                    )
                    frame.grid(row=y, column=x, padx=1, pady=1)
                    frame.grid_propagate(False)
                    CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.FRAME, value=frame)

                    if BlackCellHandler.should_create_black_cell(
                        is_open            = is_open,
                        y                  = y,
                        x                  = x,
                        black_cells        = Crossword.__black_cells,
                        current_cwc_matrix = CwcMatrix.get_row(
                            matrix_type = MatrixType.BOOLEAN,
                            y           = y),
                        max_word_len       = GlobalData.MAX_WORD_LENGTH
                    ):
                        if is_open is False:
                            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.BOOLEAN, value=0)
                        Crossword.__create_black_cell(y=y, x=x, frame=frame)
                        CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.ENTRY, value=None)
                    else:
                        if is_open is False:
                            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.BOOLEAN, value=1)
                        entry = Crossword.__create_white_cell(y=y, x=x, frame=frame, is_open=is_open)
                        CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.ENTRY, value=entry)

            if not is_open:
                BlackCellHandler.set_isolated_white_cells_to_black(
                    objects_map = Crossword.__objects_map,
                    method      = Crossword.__create_black_cell
                )

            CwcMatrix.log(matrix_type=MatrixType.VARIABLE)

            Crossword.set_font_dimension()

            Crossword.__scroll_frame.grid(
                sticky     = tk.NSEW,
                row        = 0,
                column     = 0,
                columnspan = 2,
                padx       = 10,
                pady       = 10
            )

            master.master.grid_rowconfigure   (0, weight=1)
            master.master.grid_columnconfigure(0, weight=3)
        except Exception as e:
            print(e)

    @staticmethod
    def finalize_crossword(is_open=False):
        """Removes the finalize button frame, moves the crossword a bit up, creates
        the words and sets the numbers.
        """

        # Calls "removeWidget", method added to TKinterModernThemes as not present but needed
        Crossword.__master_frame.removeWidget(widget=Crossword.__btn_frame)

        Crossword.__btn_finalize.get_button().grid_forget()
        del Crossword.__btn_finalize
        del Crossword.__btn_frame
        Crossword.__btn_frame    = None
        Crossword.__btn_finalize = None

        for bf in Crossword.__black_frames:
            try:
                bf.unbind('<Button-1>')
            except Exception:
                pass

        Crossword.__scroll_frame.grid(sticky=tk.NSEW, row=0, column=0, padx=10, pady=(66,10))
        Crossword.__create_words(is_open=is_open)
        Crossword.__set_numbers(objects_map=Crossword.__objects_map)

    @staticmethod
    def close_crossword():
        """Destroys the crossword"""

        # Calls "removeWidget", method added to TKinterModernThemes as not present but needed
        Crossword.__master_frame.removeWidget(widget=Crossword.__btn_frame)

        Crossword.__scroll_frame.grid_forget()

        if Crossword.__btn_frame:
            del Crossword.__btn_frame
            Crossword.__btn_frame    = None

        if Crossword.__btn_finalize:
            del Crossword.__btn_finalize
            Crossword.__btn_finalize = None

        Crossword.__scroll_frame.destroy()
        Crossword.__scroll_frame = None

        Crossword.emit_crossword_closed()

    @staticmethod
    def cell_inverted(*_, y, x, frame=None):
        """If crossword not yet finalized, inverts a cell (black to white and viceversa)
        when clicked. After having inverted it, calls BlackCellHandler to check if it's
        isolated and, if True, marks the cell red and disables the finalize button.
        If the cell is not isolated, enables the finalize button.
        """

        if CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x):
            cell = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=y, x=x)
            cell.grid_forget()
            cell.destroy()
            Crossword.__create_black_cell(y=y, x=x, frame=frame)
            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.VARIABLE, value=None)
            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.ENTRY   , value=None)
            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.BOOLEAN , value=0)
        else: # invert to white
            for _f in frame.children.items():
                if '!frame' in _f[0]:
                    Crossword.__black_frames.remove(_f[1])
                    _f[1].grid_forget()
                    _f[1].destroy()
                    break
            entry = Crossword.__create_white_cell(y=y, x=x, frame=frame)
            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.ENTRY, value=entry)
            CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.BOOLEAN, value=1)

        invalid_cells = BlackCellHandler.get_isolated_white_cells()

        for c in Crossword.__invalid_cells:
            cell = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=c[0], x=c[1])
            if cell:
                cell.configure(style='White.Label')

        for c in invalid_cells:
            cell = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=c[0], x=c[1])
            cell.configure(style='Red.Label')
        if len(invalid_cells) > 0:
            Crossword.__btn_finalize.get_button().configure(state='disabled')
        else:
            Crossword.__btn_finalize.get_button().configure(state='normal')

        Crossword.__invalid_cells = invalid_cells

    @staticmethod
    def set_font_dimension(*_):
        """Updates every cell dimension using get_matrix_dimensions().
        First a loop for the MatrixType.NUMBER elements to get also the height
        of the CellLabel, needed afterwards to configure the pady of the CellEntry.
        """

        if not CwcMatrix.get(matrix_type=MatrixType.ENTRY):
            return

        lbl_height = 0

        Crossword.__frame_cwc.forget()

        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                num_lbl = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=y, x=x)
                if num_lbl:
                    num_lbl.configure(
                        font=(
                            GlobalData.CURRENT_FONT_NAME,
                            get_matrix_dimensions('number_font')
                        )
                    )
                    if lbl_height == 0:
                        num_lbl.update_idletasks()
                        # needed afterwards to configure the pady
                        lbl_height = num_lbl.winfo_height() + 2

        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                cell = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=y, x=x)
                if cell:
                    cell.configure(
                        font=(
                            GlobalData.CURRENT_FONT_NAME,
                            get_matrix_dimensions('white_font'),
                            'bold'
                        )
                    )
                    if not CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=y, x=x):
                        cell.grid_configure(pady=(lbl_height, 0))

                frame = CwcMatrix.get(matrix_type=MatrixType.FRAME, y=y, x=x)
                frame.configure(
                    width  = get_matrix_dimensions('white_frame'),
                    height = get_matrix_dimensions('white_frame')
                )

                if not CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x):
                    children = frame.winfo_children()
                    black_frames = [c for c in children if c.widgetName == 'ttk::frame']
                    if black_frames:
                        black_frames[0].configure(
                            width  = get_matrix_dimensions('black_frame'),
                            height = get_matrix_dimensions('black_frame')
                        )

        Crossword.__frame_cwc.grid(row=1, column=0)

    @staticmethod
    def refresh():
        """Reconfigure all the colors of each element of the crossword.
        Needed when changing app style or mode.
        """

        if Crossword.__frame_cwc:
            Crossword.__frame_cwc.configure(style='Custom.TFrame')
        if Crossword.__inner_frame_cwc:
            Crossword.__frame_cwc.configure(style='Custom.TFrame')
        if Crossword.__scroll_frame:
            Crossword.__scroll_frame.configure(
                fg_color               = str(Colors.label_frame_col),
                bg_color               ='transparent',
                scrollbar_button_color = Colors.very_light_grey
                    if Theme.CURRENT_APP_MODE == 'light'
                    else Colors.grey
            )
        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                lbl = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=y, x=x)
                if lbl:
                    lbl.configure(background=Colors.white, foreground=Colors.black)
                entry = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=y, x=x)
                if entry:
                    entry.configure(background=Colors.white, foreground=Colors.black)

    @staticmethod
    def __create_finalize_btn_frame(master):
        """Creates the finalize button and it's frame."""

        Crossword.__btn_frame = WidgetFrame(master=master, name='Crossword.__btn_frame')

        Crossword.__btn_finalize = CwcButtonTkmt(
            master          = Crossword.__btn_frame,
            text            = gtbk('finalize_cw'),
            image_base_name = 'save',
            command         = Crossword.emit_finalize_crossword,
            row             = 0,
            col             = 0,
            padx            = 5,
            pady            = 10,
            sticky          = tk.NS,
            style           = 'Toolbutton',
            compound        = tk.LEFT
        )
        Crossword.__btn_finalize.get_button().grid(row=0, column=0)

    @staticmethod
    def __create_black_cell(y, x, frame):
        """Creates a black cell."""

        CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.VARIABLE, value=None)
        width = height = get_matrix_dimensions('black_frame')
        black_frame    = ttk.Frame(
            master      = frame,
            relief      = tk.SOLID,
            borderwidth = 0,
            width       = width,
            height      = height,
            style       = 'Black.TFrame'
        )
        black_frame.grid(sticky=tk.NSEW, padx=2, pady=2)
        Crossword.__black_cells.append((y, x))
        Crossword.__black_frames.append(black_frame)
        black_frame.bind(
            '<Button-1>',
            lambda event, y=y, x=x, frame=frame : Crossword.cell_inverted(y=y, x=x, frame=frame))

    @staticmethod
    def __create_white_cell(y, x, frame, is_open=False):
        """Creates a white cell."""

        var = None

        if is_open:
            var = CwcMatrix.get(matrix_type=MatrixType.VARIABLE, y=y, x=x)

        if not var or not isinstance(var, tk.StringVar):
            var = tk.StringVar()
            CwcMatrix.set(matrix_type=MatrixType.VARIABLE, y=y, x=x, value=var)

        entry = CellEntry(master=frame, y=y, x=x, textvariable=var)
        Crossword.__objects_map.append({'coord' : (y, x), 'frm' : frame, 'entry' : entry})
        entry.grid(sticky=tk.NSEW, padx=0, pady=0, row=1, column=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        entry.configure(style='White.Label', justify='center')
        entry.set_highlighter()
        entry.bind('<Button-1>', lambda event, y=y, x=x, frame=frame :
            Crossword.cell_inverted(y=y, x=x, frame=frame))
        return entry

    @staticmethod
    def __set_numbers(objects_map):
        """Sets the number to all the "starting word" cells of the matrix
        adding a CellLabel to the cell frame.
        At the first CellLabel set, it calculates the height of the label to be
        able, afterwards, to configure the pady of all the cells without a number.
        This is needed to align the text of all the cells, those with a number and those without.
        """
        try:
            sorted_coordinates = Crossword.__get_sorted_words_coordinates()

            num        = 1
            lbl_height = 0

            for y in range(GlobalData.TOT_ROWS):
                for x in range(GlobalData.TOT_COLS):
                    if (y, x) in sorted_coordinates:
                        for o in objects_map:
                            if o['coord'] != (y, x):
                                continue
                            try:
                                cl = CellLabel(master=o['frm'], y=y, x=x, justify=tk.LEFT)
                                cl.grid(sticky=tk.NSEW, padx=1, pady=1, row=0, column=0)
                                cl.configure(
                                    background = Colors.white,
                                    foreground = Colors.black,
                                    padding    = 0,
                                    text       = str(num)
                                )
                                cl.set_highlighter()
                                if lbl_height == 0:
                                    cl.update_idletasks()
                                    # needed afterwards to configure the pady
                                    lbl_height = cl.winfo_height() + 2
                                for word in o['entry'].words():
                                    cl.add_word(w=word)
                                num += 1
                                CwcMatrix.set(
                                    y           = y,
                                    x           = x,
                                    matrix_type = MatrixType.NUMBER,
                                    value       = cl
                                )
                            except Exception as e:
                                print(e)
                            break
                    else:
                        CwcMatrix.set(
                            y           = y,
                            x           = x,
                            matrix_type = MatrixType.NUMBER,
                            value       = None
                        )

            # configure the pady of all the cells without a number
            for o in objects_map:
                if o['coord'] in sorted_coordinates:
                    continue
                if not CwcMatrix.get(
                    matrix_type = MatrixType.BOOLEAN,
                    y           = o['coord'][0],
                    x           = o['coord'][1]
                ): continue
                entry = CwcMatrix.get(
                    matrix_type = MatrixType.ENTRY,
                    y           = o['coord'][0],
                    x           = o['coord'][1]
                )
                entry.grid_configure(pady=(lbl_height, 0))
        except Exception as e:
            print(f'Error setting numbers: {e}')

    @staticmethod
    def __get_sorted_words_coordinates() -> list[tuple[int, int]]:
        """Return the sorted list of the words coordinates."""
        try:
            cells_done         = []
            cells_with_numbers = []

            for w in GlobalData.words:
                to_do = True
                for value in cells_done:
                    if value['x'] == w.get_x() and value['y'] == w.get_y():
                        to_do = False
                        break
                if to_do:
                    cells_done.append({'y': w.get_y(), 'x' : w.get_x()})
                    cells_with_numbers.append((w.get_y(), w.get_x()))
            cells_with_numbers.sort(key = operator.itemgetter(0, 1))
            return cells_with_numbers
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def __create_words(is_open=False):
        """Creates all the word objects of the matrix.
        IS_OPEN True means the words are already created in GlobalData.words as loaded
        IS_OPEN False means the words need to be created
        There are 2 semi identical cycles that "cannot" be merged into one because they
        are inverted. The first is Y -> X, the second is X -> Y.
        """

        if is_open is False:
            clear_words()

        # HORIZONTAL WORDS
        for y in range(GlobalData.TOT_ROWS):
            start_found = False
            start_x     = 0
            _word       = ''
            for x in range(GlobalData.TOT_COLS):
                is_black = CwcMatrix.get(
                    matrix_type = MatrixType.BOOLEAN,
                    y           = y,
                    x           = x
                ) == 0
                if start_found is False:
                    if is_black:
                        continue
                    if x < (GlobalData.TOT_COLS - 1) and \
                        CwcMatrix.get(
                            matrix_type = MatrixType.BOOLEAN,
                            y           = y,
                            x           = x + 1
                        ) == 1: # check if len(_word) > 1
                        start_found = True
                        start_x     = x
                        _word += CwcMatrix.get_variable_value(
                            y                           = y,
                            x                           = x,
                            convert_empty_to_underscore = True
                        )
                else: # start_found == True
                    if is_black or x == GlobalData.TOT_COLS - 1:
                        if not is_black:
                            _word += CwcMatrix.get_variable_value(
                                y                           = y,
                                x                           = x,
                                convert_empty_to_underscore = True
                            )
                        if len(_word) > 1:
                            if is_open is False:
                                w = Word(
                                    coordinates = (y, start_x),
                                    length      = len(_word),
                                    word        = _word,
                                    direction   = Direction.HORIZONTAL
                                )
                                GlobalData.words.append(w)
                            else:
                                w = get_word_by_coord_and_direction(
                                    coord     = (y, start_x),
                                    direction = Direction.HORIZONTAL
                                )
                            CwcMatrix.get(
                                matrix_type = MatrixType.ENTRY,
                                y           = y,
                                x           = start_x
                            ).add_word(w=w)
                            start_found = False
                            _word       = ''
                    else:
                        _word += CwcMatrix.get_variable_value(
                            y                           = y,
                            x                           = x,
                            convert_empty_to_underscore = True
                        )

        # VERTICAL WORDS
        for x in range(GlobalData.TOT_COLS):
            start_found = False
            start_y     = 0
            _word       = ''
            for y in range(GlobalData.TOT_ROWS):
                is_black = CwcMatrix.get(
                    matrix_type = MatrixType.BOOLEAN,
                    y           = y,
                    x           = x
                ) == 0
                if start_found is False:
                    if is_black:
                        continue
                    if y < (GlobalData.TOT_ROWS - 1) and \
                        CwcMatrix.get(
                            matrix_type = MatrixType.BOOLEAN,
                            y           = y + 1,
                            x           = x
                        ): # check if len(_word) > 1
                        start_found = True
                        start_y     = y
                        _word      +=  CwcMatrix.get_variable_value(
                            y                           = y,
                            x                           = x,
                            convert_empty_to_underscore = True
                        )
                else: # start_found == True
                    if is_black or y == GlobalData.TOT_ROWS - 1:
                        if not is_black:
                            _word += CwcMatrix.get_variable_value(
                                y                           = y,
                                x                           = x,
                                convert_empty_to_underscore = True
                            )
                        if len(_word) > 1:
                            if is_open is False:
                                w = Word(
                                    coordinates = (start_y, x),
                                    length      = len(_word),
                                    word        = _word,
                                    direction   = Direction.VERTICAL
                                )
                                GlobalData.words.append(w)
                            else:
                                w = get_word_by_coord_and_direction(
                                    coord     = (start_y, x),
                                    direction = Direction.VERTICAL
                                )
                            CwcMatrix.get(
                                matrix_type = MatrixType.ENTRY,
                                y           = start_y,
                                x           = x
                            ).add_word(w=w)
                            start_found = False
                            _word       = ''
                    else:
                        _word += CwcMatrix.get_variable_value(
                            y                           = y,
                            x                           = x,
                            convert_empty_to_underscore = True
                        )


############# TESTS #############

def test():
    Theme.CURRENT_APP_MODE = 'dark'
    GlobalData.main_window.tk.call("set_theme", Theme.CURRENT_APP_MODE)
    Crossword.refresh()

def finalize():
    from cell_handler import CellHandler

    Crossword.finalize_crossword()
    bind(CellHandler, lambda *args, **kargs: print('emit_highlighted_word')  , 'emit_highlighted_word')
    bind(CellHandler, lambda *args, **kargs: print('emit_unhighlighted_word'), 'emit_unhighlighted_word')
    CellHandler().bind_events()

if __name__ == "__main__":
    from cwc_style    import set_style

    set_style()

    f = GlobalData.main_tkmt_window.addLabelFrame("TEST", sticky=tk.NSEW, padx=2, pady=2, row=0, col=0)
    bind(Crossword, lambda *args, **kargs : finalize(), 'emit_finalize_crossword')
    Crossword.create_crossword(master=f)
    GlobalData.main_tkmt_window.Button(text='Refresh', command=test)
    GlobalData.main_tkmt_window.run()
