""" Module to handle the matricies.
"""

import tkinter as tk
from enum import Enum

from tkinter import ttk

from cwc_globals import GlobalData

class MatrixType(Enum):
    BOOLEAN      = 1
    VARIABLE     = 2
    NUMBER       = 3
    ENTRY        = 4
    FRAME        = 5
    TMPL_BOOLEAN = 6
    TMPL_FRAME   = 7

class CwcMatrix:
    """ Class to handle the matricies. """

    __boolean_matrix     :list[int         ] = [] # True for black cells, False for white cells
    __cell_var_matrix    :list[tk.StringVar] = [] # variable for each white cell
    __cell_num_matrix    :list[ttk.Label   ] = [] # label for the number of each white cell with a word starting from it
    __cell_entry_matrix  :list[ttk.Entry   ] = [] # entry for each white cell
    __cell_frame_matrix  :list[ttk.Frame   ] = [] # frame for each cell (black or white)
    __tmpl_boolean_matrix:list[int         ] = [] # Template - True for black cells, False for white cells
    __tmpl_frame_matrix  :list[ttk.Frame   ] = [] # Template - frame for each cell (black or white)

    @staticmethod
    def clear(matrix_type:MatrixType):
        match matrix_type:
            case MatrixType.BOOLEAN:
                CwcMatrix.__boolean_matrix.clear()
            case MatrixType.VARIABLE:
                CwcMatrix.__cell_var_matrix.clear()
            case MatrixType.NUMBER:
                CwcMatrix.__cell_num_matrix.clear()
            case MatrixType.ENTRY:
                CwcMatrix.__cell_entry_matrix.clear()
            case MatrixType.FRAME:
                CwcMatrix.__cell_frame_matrix.clear()
            case MatrixType.TMPL_BOOLEAN:
                CwcMatrix.__tmpl_boolean_matrix.clear()
            case MatrixType.TMPL_FRAME:
                CwcMatrix.__tmpl_frame_matrix.clear()

    @staticmethod
    def clear_matrices():
        """Clears all the matrices"""

        CwcMatrix.__boolean_matrix     .clear()
        CwcMatrix.__cell_var_matrix    .clear()
        CwcMatrix.__cell_num_matrix    .clear()
        CwcMatrix.__cell_entry_matrix  .clear()
        CwcMatrix.__cell_frame_matrix  .clear()
        CwcMatrix.__tmpl_boolean_matrix.clear()
        CwcMatrix.__tmpl_frame_matrix  .clear()

    @staticmethod
    def log(matrix_type=None):
        if not matrix_type:
            for mt in [
                MatrixType.BOOLEAN     ,
                MatrixType.VARIABLE    ,
                MatrixType.NUMBER      ,
                MatrixType.ENTRY       ,
                MatrixType.FRAME       ,
                MatrixType.TMPL_BOOLEAN,
                MatrixType.TMPL_FRAME
            ]:
                CwcMatrix.log(matrix_type=mt)

        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                match matrix_type:
                    case MatrixType.BOOLEAN | MatrixType.TMPL_BOOLEAN:
                        print(CwcMatrix.get(matrix_type=matrix_type, y=y, x=x), end='')
                    case MatrixType.VARIABLE:
                        print(CwcMatrix.get_variable_value(y=y, x=x), end='')
                    case MatrixType.ENTRY | MatrixType.FRAME | MatrixType.TMPL_FRAME | MatrixType.NUMBER:
                        if CwcMatrix.get(matrix_type=matrix_type, y=y, x=x):
                            print('1', end='')
                        else:
                            print('0', end='')
                print(' ', end='')
            print('')

    @staticmethod
    def get(matrix_type:MatrixType, y=None, x=None):
        """Return the object at [Y][X] if Y and X are not None else the whole matrix"""
        matrix = None

        match matrix_type:
            case MatrixType.BOOLEAN     : matrix = CwcMatrix.__boolean_matrix
            case MatrixType.VARIABLE    : matrix = CwcMatrix.__cell_var_matrix
            case MatrixType.NUMBER      : matrix = CwcMatrix.__cell_num_matrix
            case MatrixType.ENTRY       : matrix = CwcMatrix.__cell_entry_matrix
            case MatrixType.FRAME       : matrix = CwcMatrix.__cell_frame_matrix
            case MatrixType.TMPL_BOOLEAN: matrix = CwcMatrix.__tmpl_boolean_matrix
            case MatrixType.TMPL_FRAME  : matrix = CwcMatrix.__tmpl_frame_matrix

        if  matrix          and \
            y is not None   and \
            x is not None   and \
            len(matrix) > y and \
            len(matrix[y]) > x: \
            return matrix[y][x]
        return matrix

    @staticmethod
    def get_row(matrix_type:MatrixType, y):
        """Return the Y row of the matrix specified by MATRIX_TYPE"""

        matrix = CwcMatrix.get(matrix_type)
        return matrix[y] if matrix and len(matrix) > y else None

    @staticmethod
    def set(matrix_type:MatrixType, y, x, value, default_value=None):
        """Set's VALUE to matrix of MATRIX_TYPE at [Y][X].
        If row Y (and previous) is not present, will be created.
        If column X (and previous) is not present, will be created.
        """
        try:
            matrix = CwcMatrix.get(matrix_type)
            while len(matrix) <= y:
                matrix.append([])
                if default_value:
                    matrix[len(matrix)-1].extend([default_value for _ in range(GlobalData.TOT_COLS)])
            while len(matrix[y]) < x:
                matrix[y].append(default_value)
            if len(matrix[y]) == x:
                matrix[y].append(value)
            else:
                matrix[y][x] = value
        except Exception as e:
            print(e)

    @staticmethod
    def set_all(matrix_type:MatrixType, value):
        matrix = CwcMatrix.get(matrix_type) or []
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                CwcMatrix.set(matrix_type=matrix_type, y=y, x=x, value=value)

    @staticmethod
    def copy_from_matrix(source_matrix, matrix_type:MatrixType, clear=True, dest_y=0, dest_x=0, default_value=None):
        """Copy the whole SOURCE_MATRIX to the matrix specified by MATRIX_TYPE"""

        if clear:
            m = CwcMatrix.get(matrix_type=matrix_type)
            if m:
                m.clear()

        for y, _ in enumerate(source_matrix):
            for x, _ in enumerate(source_matrix[0]):
                if y + dest_y < GlobalData.TOT_ROWS and x + dest_x < GlobalData.TOT_COLS:
                    CwcMatrix.set(
                        matrix_type   = matrix_type,
                        y             = y+dest_y,
                        x             = x+dest_x,
                        value         = source_matrix[y][x],
                        default_value = default_value
                    )

    @staticmethod
    def get_variable_value(y, x, convert_empty_to_underscore=False):
        """Return the value at [Y][X] from MatrixType.VARIABLE.
        If CONVERT_EMPTY_TO_UNDERSCORE is True, return '_' if value is ''
        """

        try:
            matrix = CwcMatrix.get(MatrixType.VARIABLE)
            if matrix and len(matrix) > y and len(matrix[y]) > x:
                var   = matrix[y][x]
                value = var.get() if var else ''
                return '_' if convert_empty_to_underscore and value == '' else value
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def set_variable_value(y, x, value):
        """Set [Y][X] of MatrixType.VARIABLE to VALUE"""

        try:
            matrix = CwcMatrix.get(MatrixType.VARIABLE)
            if matrix and len(matrix) > y and len(matrix[y]) > x and matrix[y][x]:
                matrix[y][x].set(value)
        except Exception as e:
            CwcMatrix.log(matrix_type=MatrixType.VARIABLE)
            print(e)


############# TESTS #############

if __name__ == '__main__':
    for _y in range(GlobalData.TOT_ROWS):
        for _x in range(GlobalData.TOT_COLS):
            CwcMatrix.set(y=_y, x=_x, matrix_type=MatrixType.TMPL_BOOLEAN, value=_x)

    CwcMatrix.copy_from_matrix(
        source_matrix = CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN),
        matrix_type   = MatrixType.BOOLEAN
    )

    if CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN) != \
       CwcMatrix.get(matrix_type=MatrixType.BOOLEAN):
        print('copy_from_matrix ERROR')

    CwcMatrix.copy_from_matrix(
        source_matrix = CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN),
        matrix_type   = MatrixType.BOOLEAN,
        dest_y        = 1,
        dest_x        = 1,
        default_value = 1
    )

    debug = CwcMatrix.get(matrix_type=MatrixType.BOOLEAN)

    if CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN) == \
       CwcMatrix.get(matrix_type=MatrixType.BOOLEAN):
        print('copy_from_matrix ERROR')

    CwcMatrix.set(y=0, x=0, matrix_type=MatrixType.BOOLEAN, value=1)
    CwcMatrix.set(y=0, x=1, matrix_type=MatrixType.BOOLEAN, value=0)
    CwcMatrix.set(y=1, x=0, matrix_type=MatrixType.BOOLEAN, value=1)
    CwcMatrix.set(y=1, x=1, matrix_type=MatrixType.BOOLEAN, value=0)
    print(CwcMatrix.get(y=0, x=0, matrix_type=MatrixType.BOOLEAN))
    print(CwcMatrix.get(y=0, x=1, matrix_type=MatrixType.BOOLEAN))
    print(CwcMatrix.get(y=1, x=0, matrix_type=MatrixType.BOOLEAN))
    print(CwcMatrix.get(y=1, x=1, matrix_type=MatrixType.BOOLEAN))

    tk.Tk()

    textvariable1=tk.StringVar(value='A')
    textvariable2=tk.StringVar(value='B')
    textvariable3=tk.StringVar(value='C')
    textvariable4=tk.StringVar(value='D')

    CwcMatrix.set(y=0, x=0, matrix_type=MatrixType.ENTRY, value=ttk.Entry(textvariable=textvariable1))
    CwcMatrix.set(y=0, x=1, matrix_type=MatrixType.ENTRY, value=ttk.Entry(textvariable=textvariable2))
    CwcMatrix.set(y=1, x=0, matrix_type=MatrixType.ENTRY, value=ttk.Entry(textvariable=textvariable3))
    CwcMatrix.set(y=1, x=1, matrix_type=MatrixType.ENTRY, value=ttk.Entry(textvariable=textvariable4))
    print(CwcMatrix.get(y=0, x=0, matrix_type=MatrixType.ENTRY).get())
    print(CwcMatrix.get(y=0, x=1, matrix_type=MatrixType.ENTRY).get())
    print(CwcMatrix.get(y=1, x=0, matrix_type=MatrixType.ENTRY).get())
    print(CwcMatrix.get(y=1, x=1, matrix_type=MatrixType.ENTRY).get())
