"""
This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to search words related to a specific word"""

#TODO: maybe find a way to allow the user to add a personalized search type

import tkinter as tk

import pyperclip

from customtkinter import CTkTextbox

from cwc_globals import (
    GlobalData,
    Colors,
    Direction
)

from db_connection  import DbConnection
from cwc_toplevel   import CwcTopLevel
from word           import Word
from cwc_button     import CwcButtonTkmt
from translations   import gtbk

SEARCH_ENDS_WITH_QUERY   = """SELECT UPPER(value) FROM word WHERE UPPER(value) LIKE UPPER('%{word}'   ) ORDER BY 1"""
SEARCH_STARTS_WITH_QUERY = """SELECT UPPER(value) FROM word WHERE UPPER(value) LIKE UPPER('{word}%'   ) ORDER BY 1"""
SEARCH_CONTAINS_QUERY    = """SELECT UPPER(value) FROM word WHERE UPPER(value) LIKE UPPER('_%{word}%_') ORDER BY 1"""

SEARCH_ANAGRAMS_MAIN_QUERY      = """SELECT UPPER(value) FROM word WHERE LENGTH (value) = {length} """
SEARCH_ANAGRAMS_INNER_QUERY     = """AND value LIKE {q} """
SEARCH_ANAGRAMS_INNER_NOT_QUERY = """AND value NOT LIKE '%{c}%' """

SEARCH_ALL_CHARS_QUERY = """SELECT UPPER(value) FROM word WHERE UPPER(value) LIKE UPPER('{word}') ORDER BY 1"""

"""To find anagrams, needed to create the sql query using SEARCH_ANAGRAMS_INNER_NOT_QUERY"""
ALL_LETTERS = "abcdefghijklmnopqrstuvwxyz"

class SqlSearchFrame:
    """Class to search words related to a specific word"""

    def __init__(self, word:Word):
        self.window           = CwcTopLevel(title=gtbk('sql_search_title'), center=False)
        self.current_query    = tk.StringVar()
        self.entry:CTkTextbox = None
        self.copy_btn         = None
        self.word             = word
        self.current_row      = -1
        self.selected_text    = ''

        self.__create()

    def show(self):
        self.window.show(center_to_screen=False)

    def __create(self):
        self.window.frame().Label(
            text         = gtbk('words_search'),
            size         = 10,
            padx         = 50,
            pady         = 5,
            row          = self.__get_next_row(),
            col          = 0,
            colspan      = 3,
            sticky       = tk.NSEW,
            widgetkwargs = {'anchor' : tk.CENTER}
        )
        self.window.frame().Label(
            text         = self.word.get_word(),
            size         = 10,
            padx         = 50,
            pady         = 5,
            row          = self.__get_next_row(),
            col          = 0,
            colspan      = 3,
            sticky       = tk.NSEW,
            widgetkwargs = {'anchor' : tk.CENTER, 'foreground' : str(Colors.blue)}
        )

        self.window.frame().Seperator(padx=10, pady=3, row=self.__get_next_row(), col=0, colspan=3)

        self.window.frame().Label(
            text         = gtbk('search_type'),
            size         = 9,
            padx         = 10,
            pady         = (5,0),
            row          = self.__get_next_row(),
            col          = 0,
            sticky       = tk.EW,
            widgetkwargs = {'anchor' : tk.CENTER}
        )

        self.window.frame().Combobox(
            values       = [
                '',
                gtbk('ends_with'  ),
                gtbk('starts_with'),
                gtbk('contains'   ),
                gtbk('anagrams'   ),
                gtbk('all_chars'  )
            ],
            variable     = self.current_query,
            padx         = 10,
            pady         = 10,
            sticky       = tk.EW,
            row          = self.__get_next_row(),
            col          = 0,
            widgetkwargs = {'width': 15, 'state' : 'readonly', 'font' : GlobalData.SMALL_COMBO_FONT}
        )

        self.window.frame().Label(
            text         = gtbk('results'),
            size         = 9,
            padx         = 10,
            pady         = (5,0),
            row          = self.__get_next_row(),
            col          = 0,
            sticky       = tk.EW,
            widgetkwargs = {'anchor' : tk.CENTER}
        )

        entry_row = self.__get_next_row()

        self.entry = CTkTextbox(
            master     = self.window.frame().master,
            fg_color   = str(Colors.light_grey),
            text_color = str(Colors.dark_grey),
            height     = 100,
            width      = 20
        )
        self.entry.bind("<Button-1>", self.__click_event)

        self.entry.grid(padx=10, pady=5, row=entry_row, column=0, sticky=tk.NSEW)

        self.copy_btn = CwcButtonTkmt(
            master          = self.window.frame(),
            text            = gtbk('copy'),
            command         = lambda: pyperclip.copy(self.selected_text),
            padx            = 0,
            pady            = 0,
            row             = self.__get_next_row(),
            col             = 0,
            state           = 'disabled'
        )

        self.window.frame().Seperator(padx=10, pady=3, row=self.__get_next_row(), col=0)

        self.window.frame().master.grid_rowconfigure(entry_row, weight=1)
        self.window.frame().master.grid_columnconfigure(0, weight=1)

        CwcButtonTkmt(
            master          = self.window.frame(),
            image_base_name = 'close',
            command         = self.window.quit,
            padx            = 0,
            pady            = 0,
            row             = self.__get_next_row(),
            col             = 0,
            size            = 24,
            style           = 'Toolbutton'
        )

        self.current_query.trace_add('write', self.__on_query_change)

    def __click_event(self, event):
        self.entry.tag_remove("select", "1.0", tk.END)

        start = self.entry.index(f"@{event.x},{event.y} wordstart")
        end   = self.entry.index(f"@{event.x},{event.y} wordend")
        self.selected_text = self.entry.get(index1=start, index2=end).strip()
        if self.selected_text != '':
            self.entry.tag_add("select", start, end)
        self.copy_btn.configure(state='normal' if self.selected_text != '' else 'disabled')
        return "break"

    def __on_query_change(self, *_):
        query = ''
        words = []

        if self.current_query.get() == gtbk('ends_with'):
            query = SEARCH_ENDS_WITH_QUERY.format(word=self.word.word)
        elif self.current_query.get() == gtbk('starts_with'):
            query = SEARCH_STARTS_WITH_QUERY.format(word=self.word.word)
        elif self.current_query.get() == gtbk('contains'):
            query = SEARCH_CONTAINS_QUERY.format(word=self.word.word)
        elif self.current_query.get() == gtbk('anagrams'):
            words = self.__get_anagrams()
        elif self.current_query.get() == gtbk('all_chars'):
            words = self.__get_all_chars()

        if not words:
            words = DbConnection().get_words_by_query(query=query)
        self.entry.delete(index1=0.0, index2=tk.END)

        self.entry.tag_config('select' , background=str(Colors.light_yellow))
        self.entry.tag_config('start'  , font=GlobalData.VALUE_FONT_BOLD, foreground=str(Colors.blue))
        self.entry.tag_config('start2' , font=GlobalData.VALUE_FONT_BOLD, foreground=str(Colors.red))
        l = self.word.get_length()

        row = 1
        for w in words:
            if w == self.word.get_word():
                continue
            self.entry.insert(index=tk.END, text=f'{w}\n')

            if self.current_query.get() == gtbk('all_chars'):
                self.__tag_all_chars(w=w, row=row)

            elif self.current_query.get() != gtbk('anagrams'):
                start_index = w.find(self.word.get_word())
                self.entry.tag_add('start', f'{row}.{start_index}', f'{row}.{start_index + l}')
            row += 1

    def __tag_all_chars(self, w, row):
        word         = self.word.get_word()
        source_index = 0

        for index, c in enumerate(w):
            if not c in self.word.get_word() or source_index >= len(word) or c != word[source_index]:
                self.entry.tag_add('start2', f'{row}.{index}', f'{row}.{index + 1}')
            else:
                self.entry.tag_add('start', f'{row}.{index}', f'{row}.{index + 1}')
                source_index +=1

    def __get_anagrams(self) -> list[str]:
        query = self.__create_anagram_query()
        return DbConnection().get_words_by_query(query=query)

    def __get_all_chars(self) -> list[str]:
        query = self.__create_all_chars_query()
        return DbConnection().get_words_by_query(query=query)

    def __create_anagram_query(self):
        query = SEARCH_ANAGRAMS_MAIN_QUERY.format(length=self.word.length)

        word = self.word.get_word().lower()

        chars_counted = []
        for c in word:
            if c not in chars_counted:
                chars_counted.append(c)
                inner_query = "'"
                count = word.count(c)
                for _ in range(count):
                    inner_query += f"%{c.lower()}"
                inner_query += "%'"
                query += SEARCH_ANAGRAMS_INNER_QUERY.format(q=inner_query)

        for c in ALL_LETTERS:
            if c not in word:
                query += SEARCH_ANAGRAMS_INNER_NOT_QUERY.format(c=c)

        return query

    def __create_all_chars_query(self):
        word = self.word.get_word()
        search_word = ''
        for c in word:
            search_word += f'%{c}'
        search_word += '%'

        query = SEARCH_ALL_CHARS_QUERY.format(word=search_word)

        return query

    def __get_next_row(self):
        self.current_row += 1
        return self.current_row

############# TESTS #############

if __name__ == "__main__":
    _w = Word(
        coordinates = (0, 0),
        word        = 'TATUAI',
        length      = 6,
        direction   = Direction.HORIZONTAL
    )

    sql_search = SqlSearchFrame(word=_w)
    sql_search.show()
