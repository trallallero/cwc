"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to create the template for the crossword generation.

"""

import os
import json
from datetime import datetime
import tkinter as tk
import jsonpickle
from TKinterModernThemes.WidgetFrame import WidgetFrame
import customtkinter as ctk

from cwc_globals import (
    GlobalData,
    Colors,
    bind,
    get_image,
    save_frame_as_image
)

from cwc_matrix import (
    MatrixType,
    CwcMatrix
)

from cwc_toplevel       import CwcTopLevel
from black_cell_handler import BlackCellHandler
from cwc_button         import CwcButtonTkmt
from popup_menu         import PopupMenu
from translations       import gtbk

class TemplateGenerator(CwcTopLevel):
    """Class to create the template for the crossword generation.
    The user can create a pattern and choose a way to fill the crossword with it.
    """

    def __init__(self):
        self.tmpl_frame   :ctk.CTkFrame        = None
        self.template_frame:WidgetFrame        = None
        self.arch_frame:ctk.CTkScrollableFrame = None
        self.ok_btn:CwcButtonTkmt              = None
        self.dim_y                             = tk.IntVar()
        self.dim_x                             = tk.IntVar()
        self.repeat                            = tk.IntVar()
        self.cell_size                         = 20 # TODO: dynamic?
        self.__templ_row                       = -1
        self.__block_signals                   = False

        super().__init__(center=False)

        self.__create()

    def get_template(self):
        self.show()
        return self.cancel is False

    def __create(self):
        self.__create_file_frame    (master=self.frame(), row=0)
        self.__create_template_frame(master=self.frame(), row=1)
        self.__create_preview_frame (master=self.frame(), row=1)
        self.__create_buttons_frame (master=self.frame(), row=2)

    def __create_file_frame(self, master:WidgetFrame, row):
        file_frame = master.addLabelFrame(
            text         = f" {gtbk('archive')} ",
            widgetkwargs = {'relief': tk.SOLID, 'height' : 50},
            row          = row,
            col          = 0,
            colspan      = 2,
            padx         = 10,
            pady         = 10
        )
        self.arch_frame = ctk.CTkScrollableFrame(
            master                       = file_frame.master,
            orientation                  = 'horizontal',
            fg_color                     = 'transparent',
            border_color                 = Colors.light_grey,
            scrollbar_button_hover_color = Colors.orange,
            height                       = 60,
            border_width                 = 0
        )
        self.arch_frame.grid(padx=3, pady=3, row=0, column=0, sticky=tk.EW)
        file_frame.master.grid_rowconfigure(0, weight=0)
        file_frame.master.grid_columnconfigure(0, weight=1)

        settings = self.__get_saved_templates()

        col = 0
        for s in settings:
            try:
                self.__add_template_to_file_frame(s=s, col=col)
                col += 1
            except Exception as e:
                self.menu_method(key='delete', widget=None, path=s['p'])
                print(e)

    def __add_template_to_file_frame(self, s, col):
        lbl = ctk.CTkLabel(
            master   = self.arch_frame,
            text     = f"{s['y']} x {s['x']} : {s['r']}",
            font     = GlobalData.SMALL_FONT,
            compound = tk.TOP,
            width    = 30,
            height   = 30,
            cursor   = 'hand2',
            image    = get_image(s['p'], size=50)
        )
        lbl.grid(padx=10, row=0, column=col)
        lbl.bind('<Button-1>', lambda *_, p=s['p'] : self.__load_template  (path=p))
        lbl.bind('<Button-3>', lambda e , p=s['p'] : self.__delete_template(widget=e.widget, path=p))

    def __create_template_frame(self, master:WidgetFrame, row):
        self.template_frame = master.addLabelFrame(
            text         = f" {gtbk('templates')} ",
            widgetkwargs = {'relief': tk.SOLID},
            row          = row,
            col          = 0,
            padx         = 10,
            pady         = 10
        )

        self.template_frame.Label(text=GlobalData.VERT_ARROW, size=14, row=self.__get_next_tmpl_row(), col=0, padx=(3, 0), pady=0)
        self.template_frame.Combobox(
            values       = [str(d) for d in range(GlobalData.MIN_MAX_TMPL_DIMENSIONS[0], GlobalData.MIN_MAX_TMPL_DIMENSIONS[1] + 1)],
            variable     = self.dim_y,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'state' : 'readonly'},
            row          = self.__get_current_tmpl_row(),
            col          = 1,
            padx         = 3
        )
        self.template_frame.master.grid_rowconfigure(self.__get_current_tmpl_row(), weight=0)

        self.template_frame.Label(text=GlobalData.HORIZ_ARROW, size=14, row=self.__get_next_tmpl_row(), col=0, padx=(10, 0), pady=0)
        self.template_frame.Combobox(
            values       = [str(d) for d in range(GlobalData.MIN_MAX_TMPL_DIMENSIONS[0], GlobalData.MIN_MAX_TMPL_DIMENSIONS[1] + 1)],
            variable     = self.dim_x,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'state' : 'readonly'},
            row          = self.__get_current_tmpl_row(),
            col          = 1,
            padx         = (0, 5)
        )
        self.template_frame.master.grid_rowconfigure(self.__get_current_tmpl_row(), weight=0)

        self.template_frame.Label(text=gtbk('margin'), size=8, row=self.__get_next_tmpl_row(), col=0, padx=(3, 0), pady=0)
        self.template_frame.Combobox(
            values       = [str(d) for d in range(GlobalData.MIN_MAX_TMPL_REPEAT[0], GlobalData.MIN_MAX_TMPL_REPEAT[1] + 1)],
            variable     = self.repeat,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'state' : 'readonly'},
            row          = self.__get_current_tmpl_row(),
            col          = 1,
            padx         = 3
        )
        self.template_frame.master.grid_rowconfigure(self.__get_current_tmpl_row(), weight=0)

        self.__update_template(row=self.__get_next_tmpl_row())
        self.template_frame.master.grid_rowconfigure(self.__get_current_tmpl_row(), weight=1)

        CwcButtonTkmt(
            master          = self.template_frame,
            text            = gtbk('save'),
            command         = self.__save_template,
            pady            = (0, 5),
            row             = self.__get_next_tmpl_row(),
            col             = 0,
            columnspan      = 2,
            style           = 'Toolbutton',
            state           = 'normal'
        )

        self.template_frame.master.grid_columnconfigure(0, weight=1)
        self.template_frame.master.grid_columnconfigure(1, weight=1)

    def __create_preview_frame(self, master:WidgetFrame, row):
        preview_frame = master.addLabelFrame(
            text         = f" {gtbk('preview')} ",
            widgetkwargs = {'relief': tk.SOLID},
            row          = row,
            col          = 1,
            padx         = 10,
            pady         = 10
        )
        preview_frame.master.grid_rowconfigure   (0, weight=1)
        preview_frame.master.grid_columnconfigure(0, weight=1)

        self.__generate_crossword(
            master        = preview_frame.master,
            row           = 0,
            rows          = GlobalData.TOT_ROWS,
            cols          = GlobalData.TOT_COLS,
            bind_to_mouse = False
        )

        self.dim_y .trace_add('write', lambda *_: (self.__update_template(), self.__update_preview()))
        self.dim_x .trace_add('write', lambda *_: (self.__update_template(), self.__update_preview()))
        self.repeat.trace_add('write', self.__update_preview)

    def __create_buttons_frame(self, master:WidgetFrame, row):
        buttons_frame = ctk.CTkFrame(
            master   = master.master,
            width    = 10,
            cursor   = 'hand2',
            bg_color = 'transparent',
            fg_color = 'transparent'
        )
        buttons_frame.grid(padx=0, pady=0, row=row, column=0, columnspan=2, sticky=tk.EW)

        buttons_frame.master.grid_rowconfigure   (0, weight=0)
        buttons_frame.master.grid_columnconfigure(0, weight=1)

        wf = WidgetFrame(master=buttons_frame, name='__create_buttons_frame_wf')

        self.ok_btn = CwcButtonTkmt(
            master          = wf,
            image_base_name = 'save',
            command         = self.quit,
            padx            = 20,
            pady            = (0, 5),
            row             = 0,
            col             = 0,
            size            = 24,
            style           = 'Toolbutton',
            state           = 'disabled'
        )

        CwcButtonTkmt(
            master          = wf,
            image_base_name = 'close',
            command         = lambda : self.quit(cancel=True),
            padx            = 20,
            pady            = (0, 5),
            row             = 0,
            col             = 1,
            size            = 24,
            style           = 'Toolbutton',
            state           = 'normal'
        )

    def __load_template(self, path):
        settings = self.__get_saved_templates()
        if len(settings) == 0:
            return

        for s in settings:
            if s['p'] == path:
                self.__block_signals = True

                self.dim_y .set(s['y'])
                self.dim_x .set(s['x'])
                self.repeat.set(s['r'])

                CwcMatrix.copy_from_matrix(
                    source_matrix = jsonpickle.decode(s['m']),
                    matrix_type   = MatrixType.TMPL_BOOLEAN
                )
                self.__block_signals = False

                self.__update_template(is_open=True)
                self.__update_preview()

    def menu_method(self, key, widget, path):
        match key:
            case 'apply' :
                self.__load_template(path=path)
            case 'delete':
                if widget:
                    widget.master.grid_forget()
                    widget.master.destroy()
                    for col, c in enumerate(self.arch_frame.children.items()):
                        c[1].grid(padx=10, row=0, column=col)

                saved_settings = self.__get_saved_templates()
                if len(saved_settings) == 0:
                    return

                settings = []
                for s in saved_settings:
                    if s['p'] != path:
                        settings.append(s)

                with open(GlobalData.TEMPLATES_FILENAME, 'w', encoding='latin-1') as f:
                    json.dump(obj=settings, fp=f, indent=3)

                os.remove(path)

    def __delete_template(self, widget, path):
        pm = PopupMenu(master=widget, text_func_map={'apply' : True, 'delete' : True})
        bind(
            pm,
            lambda _, key, widget, path=path : self.menu_method(key=key, widget=widget, path=path),
            'menu_method'
        )
        pm.show()

    def __save_template(self, *_):
        settings = {}

        filename = os.path.join(
            GlobalData.ROOT_DIR,
            GlobalData.TEMPLATE_DIR,
            f'{int(datetime.now().timestamp())}.png')

        save_frame_as_image(frame=self.tmpl_frame, filename=filename)

        with open(GlobalData.TEMPLATES_FILENAME, 'r', encoding='latin-1') as f:
            settings = json.load(f)

        json_data = {
            "p" : os.path.join(GlobalData.ROOT_DIR, GlobalData.TEMPLATE_DIR, filename),
            "y" : self.dim_y.get(),
            "x" : self.dim_x.get(),
            "r" : self.repeat.get(),
            "m" : jsonpickle.encode(CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN))
        }
        settings.append(json_data)

        with open(GlobalData.TEMPLATES_FILENAME, 'w', encoding='latin-1') as f:
            json.dump(obj=settings, fp=f, indent=3)

        self.__add_template_to_file_frame(s=json_data, col=len(settings))

    def __update_template(self, *_, row=None, is_open=False):
        if self.__block_signals:
            return
        if not is_open:
            CwcMatrix.clear(matrix_type=MatrixType.TMPL_BOOLEAN)

        if not row:
            if self.tmpl_frame:
                row = self.tmpl_frame.grid_info()['row']
            else:
                row = self.__get_current_tmpl_row()

        if self.tmpl_frame:
            self.tmpl_frame.forget()
            self.tmpl_frame.destroy()

        self.tmpl_frame = self.__generate_crossword(
            master     = self.template_frame.master,
            row        = row,
            rows       = self.dim_y.get(),
            cols       = self.dim_x.get(),
            columnspan = 2,
            is_open    = is_open
        )
        # to avoid changing the size of all window,
        # set the pady of the template crossword dynamically
        pady = self.cell_size * (GlobalData.MIN_MAX_TMPL_DIMENSIONS[1] - self.dim_y.get())
        self.tmpl_frame.grid_configure(pady=(pady, 0))

    def __update_preview(self, *_):
        if self.__block_signals:
            return

        self.__generate_preview_matrix()

        for row in range(GlobalData.TOT_ROWS):
            for col in range(GlobalData.TOT_COLS):
                value = CwcMatrix.get(
                    matrix_type = MatrixType.BOOLEAN,
                    y           = row,
                    x           = col
                )
                frame = CwcMatrix.get(matrix_type=MatrixType.FRAME, y=row, x=col)
                frame.configure(background=Colors.white if value else Colors.black)

        invalid_cells = BlackCellHandler.get_isolated_white_cells()
        for c in invalid_cells:
            cell = CwcMatrix.get(matrix_type=MatrixType.FRAME, y=c[0], x=c[1])
            cell.configure(background=Colors.red)
        self.ok_btn.configure(state='normal' if len(invalid_cells) == 0 else 'disabled')

    def __generate_preview_matrix(self):
        CwcMatrix.set_all(matrix_type=MatrixType.BOOLEAN, value=1)

        tmpl_rows = self.dim_y .get()
        tmpl_cols = self.dim_x .get()
        repeat    = self.repeat.get()

        dest_points = []

        col_counter = -1
        row         = 0
        col         = 0

        while row < GlobalData.TOT_ROWS:
            for col in range(GlobalData.TOT_COLS):
                col_counter += 1
                if col_counter == 0 or (col_counter % (tmpl_cols + repeat) == 0):
                    dest_points.append((row, col))
            row += tmpl_rows

        for point in dest_points:
            CwcMatrix.copy_from_matrix(
                source_matrix = CwcMatrix.get(matrix_type = MatrixType.TMPL_BOOLEAN),
                matrix_type   = MatrixType.BOOLEAN,
                clear         = False,
                dest_y        = point[0],
                dest_x        = point[1],
                default_value = 1
            )

    def __generate_crossword(
            self,
            master,
            row,
            rows,
            cols,
            color         = Colors.black,
            columnspan    = 1,
            bind_to_mouse = True,
            is_open       = False):
        cwc_frame = ctk.CTkFrame(
            master       = master,
            fg_color     = str(color),
            border_color = Colors.blue,
            border_width = 2
        )
        cwc_frame.grid(row=row, column=0, columnspan=columnspan, padx=10, pady=10)
        cwc_frame.grid_propagate(False)
        for _row in range(rows):
            pady=(5,1) if _row == 0 else (1, 1) if _row < rows - 1 else (1, 5)
            for col in range(cols):
                padx=(5,1) if col == 0 else (1, 1) if col < cols - 1 else (1, 5)
                border_frame = tk.Frame(
                    master     = cwc_frame,
                    width      = self.cell_size,
                    height     = self.cell_size,
                    background = Colors.white
                )
                border_frame.grid(row=_row, column=col, padx=padx, pady=pady)
                border_frame.grid_columnconfigure(0, weight=1)
                border_frame.grid_rowconfigure(0, weight=1)
                border_frame.grid_propagate(False)
                inner_frame = tk.Frame(master=border_frame)
                inner_frame.grid(padx=1, pady=1, sticky=tk.NSEW)
                cwc_frame.grid_columnconfigure(col, weight=1)

                if bind_to_mouse:
                    inner_frame.bind(
                        '<Button-1>',
                        lambda e, y=_row, x=col : self.__invert_cell(w=e.widget, y=y, x=x)
                    )
                    if is_open:
                        value = CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN, y=_row, x=col)
                        inner_frame.configure(
                            cursor     = 'hand2',
                            background = Colors.white if value else Colors.black)
                    else:
                        inner_frame.configure(cursor='hand2', background=Colors.white)
                        CwcMatrix.set(matrix_type=MatrixType.TMPL_FRAME  , y=_row, x=col, value=inner_frame)
                        CwcMatrix.set(matrix_type=MatrixType.TMPL_BOOLEAN, y=_row, x=col, value=True)
                else:
                    inner_frame.configure(background=Colors.white)
                    CwcMatrix.set(matrix_type=MatrixType.FRAME, y=_row, x=col, value=inner_frame)
            cwc_frame.grid_rowconfigure(_row, weight=1)
        cwc_frame.configure(height=self.cell_size * rows)
        cwc_frame.configure(width =self.cell_size * cols)
        return cwc_frame

    def __invert_cell(self, w:tk.Frame, y, x):
        value = not CwcMatrix.get(matrix_type=MatrixType.TMPL_BOOLEAN, y=y, x=x)

        CwcMatrix.set(
            matrix_type = MatrixType.TMPL_BOOLEAN,
            y           = y,
            x           = x,
            value       = value
        )
        w.configure(background=Colors.white if value else Colors.black)

        self.__update_preview()

    def __get_next_tmpl_row(self):
        self.__templ_row += 1
        return self.__templ_row

    def __get_current_tmpl_row(self):
        return self.__templ_row

    def __get_saved_templates(self):
        try:
            with open(GlobalData.TEMPLATES_FILENAME, 'r', encoding='latin-1') as f:
                return json.load(f)
        except Exception as e:
            print(e)
            return None


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style
    set_style()

    GlobalData.TOT_ROWS = 12
    GlobalData.TOT_COLS = 10

    #tmpl_rows = 3
    #tmpl_cols = 3
    #
    #for row in range(GlobalData.TOT_ROWS):
    #    print(f'{row % tmpl_rows} ')
    #    for col in range(GlobalData.TOT_COLS):
    #        print(f'{col % tmpl_cols} ', end='')
    #    print('')

    tg = TemplateGenerator()
    tg.show()
    #GlobalData.main_window.mainloop()
