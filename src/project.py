import os
import shutil
import tkinter as tk
import glob
import tempfile
from json import loads, dumps

import numpy
import jsonpickle
import filedialpy

from cwc_globals import (
    GlobalData,
    AppState,
    get_settings,
    set_app_settings
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)
from word         import create_word_from_json
from zipper       import Zip
from translations import gtbk

class ProjectHandler:
    def __init__(self, window):
        self.window   = window
        self.pathname = ''
        self.filename = ''

        self.files_definer = {
            'boolean_matrix' : {
                'dir'         : 'matrix',
                'base_name'   : 'boolean_matrix' ,
                'ext'         : 'bin' ,
                'method_save' : self.__save_cwc_matrix,
                'method_open' : self.__open_cwc_matrix
            },
            'variable_matrix' : {
                'dir'         : 'matrix',
                'base_name'   : 'variable_matrix' ,
                'ext'         : 'bin' ,
                'method_save' : self.__save_var_matrix,
                'method_open' : self.__open_var_matrix
            },
            'words' : {
                'dir'         : 'words' ,
                'base_name'   : '{base_name}',
                'ext'         : 'json',
                'method_save' : self.__save_words,
                'method_open' : self.__open_words
            },
            'other' : {
                'dir'         : 'other',
                'base_name'   : 'other',
                'ext'         : 'json',
                'method_save' : self.__save_other,
                'method_open' : self.__open_other
            }
        }

    def __del__(self):
        print('destroying <project>')

    def save(self):
        if self.__create_project_dirs():
            for _, value in self.files_definer.items():
                path      = value['dir']
                ext       = value['ext']
                base_name = value['base_name']
                if not value['method_save'](path=path, ext=ext, base_name=base_name):
                    return
            Zip.zip_project(self.pathname, zipname=self.filename)

    def open(self):
        self.pathname = self.__get_project_dir()
        if self.pathname != '':
            for _, value in self.files_definer.items():
                path      = value['dir']
                ext       = value['ext']
                base_name = value['base_name']
                if not value['method_open'](path=path, ext=ext, base_name=base_name):
                    return False
            return True
        return False

    def __create_project_dirs(self):
        self.filename = str(filedialpy.saveFile(title=gtbk('select_file'), initial_dir=GlobalData.ROOT_DIR, filter='*.cwc'))
        if self.filename == '':
            return False
        if not self.filename.endswith('.cwc'):
            self.filename += '.cwc'

        self.pathname = os.path.join(tempfile.gettempdir(), os.path.basename(os.path.splitext(self.filename)[0]))

        if not os.path.exists(self.pathname):
            os.mkdir(self.pathname)
        else:
            shutil.rmtree(self.pathname)
            os.mkdir(self.pathname)

        for key, value in self.files_definer.items():
            path = value['dir']
            if not os.path.exists(os.path.join(self.pathname, path)):
                os.mkdir(os.path.join(self.pathname, path))

        return True

    def __save_cwc_matrix(self, path, ext, base_name):
        try:
            filename = f"{base_name}.{ext}"
            matrix = numpy.matrix(data=CwcMatrix.get(matrix_type=MatrixType.BOOLEAN), dtype=numpy.int32)
            numpy.savetxt(os.path.join(self.pathname, path, filename), matrix)
        except Exception as e:
            print(e)
            return False
        return True

    def __save_var_matrix(self, path, ext, base_name):
        try:
            filename = f"{base_name}.{ext}"
            with open(os.path.join(self.pathname, path, filename), 'w', encoding='latin-1') as f:
                for y in range(GlobalData.TOT_ROWS):
                    for x in range(GlobalData.TOT_COLS):
                        var = CwcMatrix.get_variable_value(y=y, x=x)
                        f.write(f'{var}\n')
        except Exception as e:
            print(e)
            return False
        return True

    def __save_words(self, path, ext, base_name):
        try:
            for word in GlobalData.words:
                word_filename = f"{base_name}.{ext}".format(base_name=word.get_name())
                json_string   = jsonpickle.encode(word)
                with open(os.path.join(self.pathname, path, word_filename), 'w', encoding='latin-1') as f:
                    f.write(json_string)
        except Exception as e:
            print(e)
            return False
        return True

    def __save_other(self, path, ext, base_name):
        try:
            settings = get_settings(saved=False)
            settings['current_state'] = GlobalData.current_state().name
            settings['current_dim'  ] = GlobalData.CURRENT_FONT_SIZE
            settings['current_scale'] = GlobalData.CURRENT_SCALE_VALUE
            settings['window_state' ] = GlobalData.main_window.state()
            other_filename = f"{base_name}.{ext}"
            with open(os.path.join(self.pathname, path, other_filename), 'w', encoding='latin-1') as f:
                f.write(dumps(settings))
        except Exception as e:
            print(e)
            return False
        return True

    def __get_project_dir(self):
        filename = filedialpy.openFile(title=gtbk('select_file'), initial_dir='.', filter='*.cwc')
        if filename == '':
            return ''
        projec_dir = Zip.unzip_project(zipname=filename)
        return projec_dir

    def __open_cwc_matrix(self, path, ext, base_name):
        filename = f"{base_name}.{ext}"
        matrix = numpy.loadtxt(os.path.join(self.pathname, path, filename), dtype=numpy.int32)
        if len(matrix) > 0:
            GlobalData.TOT_ROWS = len(matrix)
            GlobalData.TOT_COLS = len(matrix[0])
            for y in range(GlobalData.TOT_ROWS):
                for x in range(GlobalData.TOT_COLS):
                    CwcMatrix.set(matrix_type=MatrixType.BOOLEAN, y=y, x=x, value=int(matrix[y, x]))
            return True
        return False

    def __open_var_matrix(self, path, ext, base_name):
        filename = f"{base_name}.{ext}"
        with open(os.path.join(self.pathname, path, filename), 'r', encoding='latin-1') as f:
            for y in range(GlobalData.TOT_ROWS):
                for x, _ in enumerate(range(GlobalData.TOT_COLS)):
                    value = f.readline().strip()
                    var = tk.StringVar()
                    var.set(value)
                    CwcMatrix.set(y=y, x=x, matrix_type=MatrixType.VARIABLE, value=var)
            return True
        return False

    def __open_words(self, path, ext, base_name):
        del base_name
        try:
            for file in glob.glob(f'{os.path.join(self.pathname, path)}/*.{ext}'):
                with open(file, 'r', encoding='latin-1') as f:
                    json_string = f.read()
                    try:
                        word = jsonpickle.decode(json_string)
                    except Exception as e:
                        print(f"Error decoding JSON: {e}")
                        word = create_word_from_json(js=json_string)
                    if word:
                        GlobalData.words.append(word)
                    else:
                        return False
            return True
        except Exception as e:
            print(e)
            return False

    def __open_other(self, path, ext, base_name):
        try:
            filename = f"{base_name}.{ext}"
            with open(os.path.join(self.pathname, path, filename), 'r', encoding='latin-1') as f:
                json_vals = loads(f.read())

                # get all values in try/except to ensure a missing value (e.g. older version)
                # does not break the loading
                GlobalData.OPEN_CW_APP_STATE = AppState[
                    self.__get_json_value(
                        source        = json_vals,
                        val_name      = 'current_state',
                        default_value = AppState.AS_NONE
                    )
                ]

                GlobalData.CURRENT_FONT_SIZE = self.__get_json_value(
                    source        = json_vals,
                    val_name      = 'current_dim',
                    default_value = GlobalData.MIN_MAX_DIMENSIONS[0]
                )

                GlobalData.CURRENT_SCALE_VALUE = self.__get_json_value(
                    source        = json_vals,
                    val_name      = 'current_scale',
                    default_value = GlobalData.RESIZE_MIN_VALUE
                )

                GlobalData.WINDOW_STATE = self.__get_json_value(
                    source        = json_vals,
                    val_name      = 'window_state',
                    default_value = 'normal'
                )

                set_app_settings(settings=json_vals, set_language=True)
        except Exception as e:
            print(e)
            return False
        return True

    def __get_json_value(self, source, val_name, default_value):
        try:
            value = source[val_name]
            return value
        except Exception:
            return default_value


############# TESTS #############

if __name__ == "__main__":
    p = ProjectHandler(window=GlobalData.main_window)
    p.save()
