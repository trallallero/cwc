"""Module to handle crossword black cells creation"""

import random
from tkinter import ttk

from cwc_matrix  import (
    MatrixType,
    CwcMatrix
)

from cwc_globals import GlobalData

def matrix_bool(t, y, x): # shorter way to access matrix boolean values
    return CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x) \
        if t == MatrixType.BOOLEAN \
        else CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN, y=y, x=x)

class BlackCellHandler:
    """Module to handle crossword black cells creation"""

    @staticmethod
    def should_create_black_cell(**kargs):
        """Return if a black cell should be created"""

        try:
            is_open            = kargs['is_open']
            y                  = kargs['y']
            x                  = kargs['x']
            black_cells        = kargs['black_cells']
            current_cwc_matrix = kargs['current_cwc_matrix']
            max_word_len       = kargs['max_word_len']
        except Exception as e:
            print(e)
            return False

        if is_open:
            return matrix_bool(MatrixType.BOOLEAN, y=y, x=x) == 0
        if GlobalData.BLACK_PERCENT == 0:
            return False
        if BlackCellHandler.is_max_word_len(
            y                  = y,
            x                  = x,
            current_cwc_matrix = current_cwc_matrix,
            max_word_len       = max_word_len
        ): return True

        return random.randint(0, 12 - GlobalData.BLACK_PERCENT) == 0 and not \
            BlackCellHandler.is_cell_in_max_contiguos(coord=(y, x), black_cells=black_cells)

    @staticmethod
    def is_max_word_len(y, x, current_cwc_matrix, max_word_len):
        """Return if the current white cell exceeds MAX_WORD_LEN"""

        try:
            if x >= max_word_len:
                xx = x - 1
                _is_max_word_len = True
                for i in range(max_word_len-1):
                    if not current_cwc_matrix[xx]:
                        _is_max_word_len = False
                        break
                    xx -= 1
                if _is_max_word_len:
                    return True
            if y >= max_word_len:
                yy = y - 1
                _is_max_word_len = True
                for i in range(max_word_len-1):
                    if matrix_bool(MatrixType.BOOLEAN, y=yy, x=x) == 0:
                        _is_max_word_len = False
                        break
                    yy -= 1
                if _is_max_word_len:
                    return True
        except Exception as e:
            print(e)
        return False

    @staticmethod
    def is_cell_in_max_contiguos(coord, black_cells):
        """Return if the current black cell exceeds GlobalData.MAX_CONTIGOUS_BLACK_CELLS"""

        if len(black_cells) < 3:
            return False

        is_in_max = False

        if coord[0] > 2: # check y
            is_in_max = True
            for i in range(1, GlobalData.MAX_CONTIGOUS_BLACK_CELLS):
                if not (coord[0] - i, coord[1]) in black_cells:
                    is_in_max = False
                    break
            if is_in_max:
                return True

        if coord[1] > 2: # check x
            is_in_max = True
            for i in range(1, GlobalData.MAX_CONTIGOUS_BLACK_CELLS):
                if not (coord[0], coord[1] - i) in black_cells:
                    is_in_max = False
                    break
        return is_in_max

    @staticmethod
    def set_isolated_white_cells_to_black(objects_map, method):
        """Set isolated white cells - means surrounded by black cells and/or margins - to black"""

        cells_to_fix = BlackCellHandler.get_isolated_white_cells()

        for cell in cells_to_fix:
            #print(f'######## CELL TO FIX: {cell}')
            for o in objects_map:
                if o['coord'] == cell:
                    frame:ttk.Frame = o['frm']
                    children = frame.winfo_children()
                    entry = children[0] if children else None
                    if entry:
                        entry.grid_forget()
                        entry.destroy()
                    CwcMatrix.set(
                        y           = cell[0],
                        x           = cell[1],
                        matrix_type = MatrixType.BOOLEAN,
                        value       = 0
                    )
                    CwcMatrix.set(
                        y           = cell[0],
                        x           = cell[1],
                        matrix_type = MatrixType.ENTRY,
                        value       = None
                    )
                    method(y=cell[0], x=cell[1], frame=frame)
        return cells_to_fix

    @staticmethod
    def get_isolated_white_cells(
        matrix = CwcMatrix.get(matrix_type=MatrixType.BOOLEAN),
        _type  = MatrixType.BOOLEAN
    ):
        cells_to_fix = []

        tot_rows = len(matrix)
        if tot_rows == 0:
            return cells_to_fix
        tot_cols = len(matrix[0])
        if tot_cols == 0:
            return cells_to_fix

        for y in range(tot_rows):
            for x in range(tot_cols):
                if not matrix_bool(_type, y=y, x=x):
                    continue

                # y higher than 1 row and lower than last row
                if y > 0 and y < (tot_rows - 1):
                    # x higher than 1 col and lower than last col
                    if  x > 0                             and \
                        x < (tot_cols - 1)                and \
                        matrix_bool(_type, y-1, x  ) == 0 and \
                        matrix_bool(_type, y  , x-1) == 0 and \
                        matrix_bool(_type, y  , x+1) == 0 and \
                        matrix_bool(_type, y+1, x  ) == 0:
                        cells_to_fix.append((y, x))
                    # x at first col
                    elif x == 0                            and \
                         matrix_bool(_type, y-1, x  ) == 0 and \
                         matrix_bool(_type, y  , x+1) == 0 and \
                         matrix_bool(_type, y+1, x  ) == 0:
                        cells_to_fix.append((y, x))
                    # x at last col
                    elif x == (tot_cols - 1)               and \
                         matrix_bool(_type, y-1, x  ) == 0 and \
                         matrix_bool(_type, y  , x-1) == 0 and \
                         matrix_bool(_type, y+1, x  ) == 0:
                        cells_to_fix.append((y, x))

                # y at first row
                elif y == 0:
                    # x higher than 1 col and lower than last col
                    if x > 0                             and \
                       x < (tot_cols - 1)                and \
                       matrix_bool(_type, y  , x-1) == 0 and \
                       matrix_bool(_type, y  , x+1) == 0 and \
                       matrix_bool(_type, y+1, x  ) == 0:
                        cells_to_fix.append((y, x))
                    # x at first col
                    elif x == 0                            and \
                         matrix_bool(_type, y  , x+1) == 0 and \
                         matrix_bool(_type, y+1, x  ) == 0:
                        cells_to_fix.append((y, x))
                    # x at last col
                    elif x == (tot_cols - 1)               and \
                         matrix_bool(_type, y  , x-1) == 0 and \
                         matrix_bool(_type, y+1, x  ) == 0:
                        cells_to_fix.append((y, x))

                # y at last row
                elif y == (tot_rows - 1):
                    # x higher than 1 col and lower than last col
                    if  x > 0                             and \
                        x < (tot_cols - 1)                and \
                        matrix_bool(_type, y-1, x  ) == 0 and \
                        matrix_bool(_type, y  , x+1) == 0 and \
                        matrix_bool(_type, y  , x-1) == 0:
                        cells_to_fix.append((y, x))
                    # x at first col
                    elif x == 0                           and \
                        matrix_bool(_type, y-1, x  ) == 0 and \
                        matrix_bool(_type, y  , x+1) == 0:
                        cells_to_fix.append((y, x))
                    # x at last col
                    elif x == (tot_cols - 1)               and \
                         matrix_bool(_type, y-1, x  ) == 0 and \
                         matrix_bool(_type, y  , x-1) == 0:
                        cells_to_fix.append((y, x))
        return cells_to_fix


############# TESTS #############

if __name__ == "__main__":
    GlobalData.TOT_ROWS = 5
    GlobalData.TOT_COLS = 5

    # test isolated white cells
    print('test 0')
    _matrix = [
        [1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0],
        [1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0],
        [1, 0, 1, 0, 1]
    ]
    CwcMatrix.copy_from_matrix(source_matrix=_matrix, matrix_type=MatrixType.BOOLEAN)

    result = [
        (0, 0),
        (0, 4),
        (4, 0),
        (4, 4),

        (2, 0),
        (2, 2),
        (2, 4),

        (0, 2),
        (4, 2)
    ]
    _cell_to_fix = BlackCellHandler.get_isolated_white_cells()
    for r in result:
        if not r in _cell_to_fix:
            print(r)


    GlobalData.TOT_ROWS = 2
    GlobalData.TOT_COLS = 2

    # test isolated white cells
    print('test 1')
    _matrix = [
        [1, 0],
        [0, 1]
    ]
    CwcMatrix.copy_from_matrix(source_matrix=_matrix, matrix_type=MatrixType.BOOLEAN)
    result = [(0, 0)]
    _cell_to_fix = BlackCellHandler.get_isolated_white_cells()
    for r in result:
        if r not in _cell_to_fix:
            print(r)


    # test isolated white cells
    print('test 2')
    _matrix = [
        [0, 1],
        [1, 0]
    ]
    CwcMatrix.copy_from_matrix(source_matrix=_matrix, matrix_type=MatrixType.BOOLEAN)
    result = [(0, 1)]
    _cell_to_fix = BlackCellHandler.get_isolated_white_cells()

    for r in result:
        if r not in _cell_to_fix:
            print(r)

    # test isolated white cells
    print('test 3')
    _matrix = [
        [0, 0],
        [0, 1]
    ]
    CwcMatrix.copy_from_matrix(source_matrix=_matrix, matrix_type=MatrixType.BOOLEAN)
    result = [(1, 1)]
    _cell_to_fix = BlackCellHandler.get_isolated_white_cells()
    for r in result:
        if r not in _cell_to_fix:
            print(r)
