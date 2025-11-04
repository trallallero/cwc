"""Module for handling the input from the user."""

import tkinter as tk

import pyperclip

from cwc_globals      import GlobalData
from cwc_button       import CwcButtonTkmt
from db_connection    import DbConnection
from volatile_message import VolatileMessage
from cwc_toplevel     import CwcTopLevel
from translations     import gtbk

class InputPanel:
    """Class for handling the input from the user.
    TODO: document it
    """

    def __init__(
            self,
            title,
            current_value    = '',
            suggested_values = None,
            show_paste       = False,
            allow_type       = True
        ) -> None:
        self.title            = title
        self.current_value    = current_value
        self.suggested_values = suggested_values
        self.is_multi_line    = False
        self.value            = ''
        self.values           = []
        self.window           = CwcTopLevel(center=False)
        self.entry_variable   = tk.StringVar()
        self.entry_text       = None
        self.ok_btn           = None
        self.paste_btn        = None
        self.cancel_btn       = None
        self.value            = ''
        self.values           = []
        self.show_paste       = show_paste
        self.allow_type       = allow_type

        self.lengths = set([len(v) for v in self.suggested_values]) if self.suggested_values else []

        self.window.master.bind('<Return>', self.__close)

    def get_word(self, like, testing=False):
        if testing:
            self.suggested_values = ['aaa']
        else:
            self.suggested_values = DbConnection().get_words_by_like(like=like)
        if not self.suggested_values:
            VolatileMessage(text=gtbk('word_not_found'))
            self.window.quit()
            return ''
        return self.get_value()

    def get_value(self):
        self.__show()
        if self.suggested_values and len(self.suggested_values) > 0:
            return '' if CwcTopLevel.cancel else self.entry_variable.get().strip()
        return '' if CwcTopLevel.cancel else self.value.strip()

    def get_values(self):
        self.is_multi_line = True
        self.__show()
        return [] if CwcTopLevel.cancel else self.values

    def __show(self):
        self.window.frame().Label(text=self.title, size=10, row=0, col=0, colspan=2 + (1 if self.show_paste else 0))

        if self.suggested_values and len(self.suggested_values) > 0:
            self.entry_text = self.window.frame().Combobox(
                values       = self.suggested_values,
                variable     = self.entry_variable,
                widgetkwargs = {'width': 5, 'font' : GlobalData.SMALL_COMBO_FONT, 'state' : 'readonly'},
                row          = 1,
                col          = 0,
                colspan      = 2 + (1 if self.show_paste else 0)
            )
            self.entry_variable.trace_add('write', self.__value_selected)
            if not self.allow_type:
                self.entry_text.configure(state='readonly')
        elif self.is_multi_line:
            self.entry_text = tk.Text(self.window.frame().master, width=30, height=20)
            self.entry_text.grid(row=1, column=0, columnspan=2 + (1 if self.show_paste else 0))
        else:
            self.entry_text = self.window.frame().Entry(
                textvariable = None,
                widgetkwargs = {'width': 30},
                row          = 1,
                col          = 0,
                colspan      = 2 + (1 if self.show_paste else 0)
            )
            if self.current_value != '':
                self.entry_text.configure(textvariable=self.entry_variable, width=len(self.current_value) + 2)
                self.entry_variable.set(self.current_value)
                self.entry_text.select_range(0, len(self.current_value))

        self.entry_text.bind('<KeyRelease>', self.__enable_ok_button)
        self.entry_text.bind('<Escape>'    , self.__close)

        self.ok_btn         = CwcButtonTkmt(
            master          = self.window.frame(),
            image_base_name = 'save',
            command         = lambda sender='btn' : self.__close(sender),
            style           = 'Toolbutton',
            row             = 2,
            col             = 0,
            padx            = 10,
            pady            = 3
        )

        if self.show_paste:
            self.paste_btn = CwcButtonTkmt(
                master       = self.window.frame(),
                text         = gtbk('paste'),
                command      = self.__paste,
                style        = 'Toolbutton',
                row          = 2,
                col          = 1,
                padx         = 10,
                pady         = 3
            )

        self.cancel_btn = CwcButtonTkmt(
            master          = self.window.frame(),
            image_base_name = 'close',
            command         = self.__cancel,
            style           = 'Toolbutton',
            row             = 2,
            col             = 2 if self.show_paste else 1,
            padx            = 10,
            pady            = 3
        )

        self.__enable_ok_button()
        self.window.master.after(200, self.entry_text.focus_set)
        self.window.root.lift()
        self.window.show()

    def __value_selected(self, _='', __='', ___='', ____=''):
        self.__enable_ok_button()

    def __paste(self):
        self.entry_text.delete(0, tk.END)
        lines = pyperclip.paste().split('\n')
        for line in lines:
            self.entry_text.insert(tk.END, f'{line.strip()}\n')
        self.__enable_ok_button()

    def __enable_ok_button(self, _=''):
        if self.suggested_values and len(self.suggested_values) > 0:
            text = self.entry_variable.get()
            if (len(text) == len(self.suggested_values[0]) or self.lengths) and ' ' not in text and len(text) > 1:
                self.ok_btn.configure(state="normal")
            else:
                self.ok_btn.configure(state="disabled")
        elif self.is_multi_line:
            if self.entry_text.get('1.0', tk.END).strip() != '':
                self.ok_btn.configure(state="normal")
            else:
                self.ok_btn.configure(state="disabled")
        else:
            if self.entry_text.get() != '':
                self.ok_btn.configure(state="normal")
            else:
                self.ok_btn.configure(state="disabled")
        #self.ok_btn.refresh()

    def __close(self, sender=''):
        CwcTopLevel.cancel = False
        if self.suggested_values and len(self.suggested_values) > 0:
            self.value = self.entry_variable.get()
        elif self.is_multi_line:
            if sender != 'btn':
                return
            self.values.clear()
            for v in self.entry_text.get('1.0', tk.END).split(sep='\n'):
                if len(v.strip()) > 0:
                    self.values.append(v.strip())
        else:
            self.value = self.entry_text.get()
        self.window.quit()

    def __cancel(self):
        self.window.quit(cancel=True)


############# TESTS #############

if __name__ == "__main__":
    from cwc_style import set_style

    set_style()

    window = CwcTopLevel()

    # NOTE: for some reason, only the first call to InputPanel sets the focus to the widget
    # but this is not a problem because it's supposed to be used as a single call
    value  = InputPanel(title='Test', current_value='', show_paste=True).get_value()
    print(value)

    value = InputPanel(title='Test').get_word(like='TUBA', testing=True)
    print(value)

    values = InputPanel(title='Test', current_value='', suggested_values=['aaa', 'bbb', 'ccc']).get_value()
    print(values)
