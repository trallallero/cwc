"""Module to handle the templates to create the crossword"""

import tkinter as tk
from TKinterModernThemes.WidgetFrame import WidgetFrame

from cwc_globals import (
    GlobalData,
    Colors,
    bind,
    get_settings,
    get_black_cells_type_id
)
from cwc_button         import CwcButtonTkmt
from cwc_toplevel       import CwcTopLevel
from template_generator import TemplateGenerator
from translations       import gtbk


class CWCTemplates:
    """Class to handle the templates to create the crossword."""

    def __init__(self, master=None) -> None:
        """Initialize the gui.
        If MASTER is None, a master needs to be passed to create().
        This is useful to allow the creation of the same gui in another master
        like Settings to avoid creating the same gui.
        """
        self.dimension_y        = tk.StringVar()
        self.dimension_x        = tk.StringVar()
        self.black_cells_type   = tk.IntVar()
        self.amount_black_cells = tk.IntVar()
        self.font_size          = tk.IntVar()
        self.max_word_len       = tk.IntVar()
        self.cancel             = False
        self.cb_percent_black   = None
        self.cb_word_len        = None
        self.current_row        = 0

        self.window = CwcTopLevel(title=gtbk('templates'), center=False) if master else None

    def get_template(self):
        return self.__get_template()

    def create(self, master:WidgetFrame, row=0):
        self.current_row = row

        if self.window:
            master.Label(text=gtbk('templates'), size=10, row=self.current_row, col=0, colspan=2)
            self.current_row += 1
            master.Seperator(padx=10, pady=(0, 10), row=self.current_row, col=0, colspan=2)

        self.current_row += 1

        settings = get_settings()

        self.__create_dimensions_frame (master=master, settings=settings)
        self.__create_black_cells_frame(master=master, settings=settings)

        if self.window:
            self.__create_buttons_frame(main_frame=master)

    def __get_template(self):
        if self.window:
            self.create(master=self.window.frame())
            self.window.show()

            if CwcTopLevel.cancel is False:
                if self.black_cells_type.get() == 2:
                    GlobalData.TOT_ROWS = int(self.dimension_y.get())
                    GlobalData.TOT_COLS = int(self.dimension_x.get())

                    tg = TemplateGenerator()
                    if tg.get_template() is False:
                        return {}

                return {
                    'y'            : self.dimension_y.get(),
                    'x'            : self.dimension_x.get(),
                    'max_word_len' : self.max_word_len.get(),
                    'font'         : self.font_size.get(),
                    'black_cells'  : 0                          \
                        if self.black_cells_type.get() == 1     \
                        else self.amount_black_cells.get()      \
                            if self.black_cells_type.get() == 0
                            else -1
                }
        return {}

    def __create_dimensions_frame(self, master:WidgetFrame, settings):
        dim_frame = master.addLabelFrame(
            text         = f" {gtbk('dimensions')} ",
            widgetkwargs = {'relief': tk.SOLID},
            row          = self.current_row,
            col          = 0,
            padx         = 5,
            pady         = 0
        )

        dim_frame.Label(text=GlobalData.VERT_ARROW, size=14, row=1, col=0, padx=(3, 0), pady=0)
        dim_frame.Combobox(
            values       = [str(d) for d in range(GlobalData.MIN_MAX_DIMENSIONS[0], GlobalData.MIN_MAX_DIMENSIONS[1] + 1)],
            variable     = self.dimension_y,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'state' : 'readonly'},
            row          = 1,
            col          = 1,
            padx         = 3
        )

        dim_frame.Label(text=GlobalData.HORIZ_ARROW, size=14, row=1, col=2, padx=(10, 0), pady=0)
        dim_frame.Combobox(
            values       = [str(d) for d in range(GlobalData.MIN_MAX_DIMENSIONS[0], GlobalData.MIN_MAX_DIMENSIONS[1] + 1)],
            variable     = self.dimension_x,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'state' : 'readonly'},
            row          = 1,
            col          = 3,
            padx         = (0, 5)
        )

        self.dimension_y.set(settings['cw']['dim'][0])
        self.dimension_x.set(settings['cw']['dim'][1])

        frame = dim_frame.addFrame(
            name         = 'Settings:dim_frame',
            widgetkwargs = {'style' : 'Dynamic.TFrame'},
            row          = self.current_row+1,
            col          = 0,
            colspan      = 4,
            padx         = 5,
            pady         = 10
        )

        frame.Label(text=gtbk('text_dimensions'), weight='normal', size=10, padx=2, pady=2, sticky=tk.W, row=0, col=0)
        frame.Label(text=gtbk('max_word_length'), weight='normal', size=10, padx=2, pady=2, sticky=tk.W, row=1, col=0)

        frame.Combobox(
            values       = list(range(GlobalData.MIN_MAX_FONT_DIMENSIONS[0], GlobalData.MIN_MAX_FONT_DIMENSIONS[1] + 1)),
            variable     = self.font_size,
            padx         = 12,
            pady         = 2,
            sticky       = tk.W,
            row          = 0,
            col          = 1,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT}
        )
        self.cb_word_len = frame.Combobox(
            values       = list(range(GlobalData.MIN_MAX_WORD_LENGTH[0], GlobalData.MIN_MAX_WORD_LENGTH[1] + 1)),
            variable     = self.max_word_len,
            padx         = 12,
            pady         = 2,
            sticky       = tk.W,
            row          = 1,
            col          = 1,
            widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT}
        )

        self.max_word_len.set(settings['cw']['max_word_len'])
        self.font_size   .set(settings['cw']['font'])

    def __create_black_cells_frame(self, master:WidgetFrame, settings):
        bcell_frame = master.addLabelFrame(text=f' {gtbk("black_cells")} ', widgetkwargs={'relief': tk.FLAT}, row=self.current_row, col=1, padx=5, pady=0)
        self.current_row += 1

        frame1 = bcell_frame.addFrame('', widgetkwargs={'style' : 'Dynamic.TFrame'}, row=1, col=0, pady=0)
        bcell_frame.Seperator(row=1, col=1, sticky="ns", padx=0, pady=3)
        frame2 = bcell_frame.addFrame('', widgetkwargs={'style' : 'Dynamic.TFrame'}, row=1, col=2, pady=0)
        bcell_frame.Seperator(row=1, col=3, sticky="ns", padx=0, pady=3)
        frame3 = bcell_frame.addFrame('', widgetkwargs={'style' : 'Dynamic.TFrame'}, row=1, col=4, pady=0)

        # frame 1
        frame1.Radiobutton(text=gtbk('random'), variable=self.black_cells_type, value=0, row=0, col=0, colspan=2, padx=0, pady=5)

        frame1.Label(text='%', size=8, row=1, col=0, padx=0, pady=0, sticky=tk.W, widgetkwargs={'relief': tk.FLAT})

        self.cb_percent_black = frame1.Combobox(
            values       = list(range(GlobalData.MIN_MAX_BLACK_CELLS_AMOUNT[0], GlobalData.MIN_MAX_BLACK_CELLS_AMOUNT[1] + 1)),
            variable     = self.amount_black_cells,
            row          = 1,
            col          = 1,
            padx         = 0,
            pady         = (0, 5),
            widgetkwargs = {'width': 2, 'state' : 'disabled', 'font' : GlobalData.SMALL_COMBO_FONT}
        )
        self.amount_black_cells.set(settings['cw']['random_percent'])

        # frame 2
        frame2.Radiobutton(text=gtbk('manual'), variable=self.black_cells_type, value=1, padx=0, pady=5)

        # frame 3
        frame3.Radiobutton(text=gtbk('template'), variable=self.black_cells_type, value=2, padx=0, pady=5)

        self.black_cells_type.trace_add('write', self.__black_cells_type_selected)
        self.black_cells_type.set(get_black_cells_type_id(settings['cw']['black_cells']))

    def __create_buttons_frame(self, main_frame:WidgetFrame):
        bottom_frame = main_frame.addFrame(
            '',
            row          = 5,
            col          = 0,
            colspan      = 2,
            padx         = 5,
            pady         = (0, 5),
            use_tk       = True,
            widgetkwargs = {'relief' : tk.FLAT, 'borderwidth' : 0, 'background' : Colors.label_frame_col }
        )

        CwcButtonTkmt(
            master          = bottom_frame,
            image_base_name = 'save',
            command         = self.__accept,
            row             = 0,
            col             = 0,
            padx            = (5, 30),
            pady            = (5, 0),
            size            = 24,
            style           = 'Toolbutton'
        )
        CwcButtonTkmt(
            master          = bottom_frame,
            image_base_name = 'close',
            command         = self.__cancel,
            row             = 0,
            col             = 1,
            padx            = (30, 5),
            pady            = (5, 0),
            size            = 24,
            style           = 'Toolbutton'
        )

    def __black_cells_type_selected(self, _='', __='', ___='', ____=''):
        if self.black_cells_type.get() == 0:
            self.cb_percent_black.configure(state='readonly')
            self.cb_word_len     .configure(state='normal')
        else:
            self.cb_percent_black.configure(state='disabled')
            self.cb_word_len     .configure(state='disabled')

    def __cancel(self):
        self.window.quit(cancel=True)

    def __accept(self, _=''):
        self.window.quit(cancel=False)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style
    set_style()
    t = CWCTemplates(master=GlobalData.main_window).get_template()
    print(t)
