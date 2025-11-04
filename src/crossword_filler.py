""" Module to fill a crossword grid with words from the database. """

import tkinter as tk

from collections import defaultdict, namedtuple
from threading import Thread, Lock
from enum import Enum

import time
import sqlite3
import pyautogui

from cwc_globals import (
    GlobalData,
    Direction
)
from cwc_toplevel import CwcTopLevel
from cwc_button import CwcButtonTkmt
from translations import gtbk
from word import (
    get_word_by_coord_and_direction,
    get_not_empty_words
)

Slot = namedtuple('Slot', 'name y x direction length overlaps')

RUNNING = False

lock = Lock()

class ExcludedWhen(Enum):
    EW_NEVER   = 0, # TODO: mightbe removed
    EW_ONCE    = 1,
    EW_SESSION = 2,
    EW_ALWAYS  = 3  # TODO: not handled yet


class CrosswordFiller:
    """ Class to fill a crossword grid with words from the database. """

    __excluded_words = []

    def __init__(self, grid, bind_esc=False, testing=False):
        self.window      = CwcTopLevel(center=False, create_frame=True, bind_esc=bind_esc)
        self.__wordlists = None
        self.__grid      = [list(row) for row in grid]
        self.__h         = len(self.__grid)
        self.__w         = max(len(row) for row in self.__grid)
        self.lengths     = []
        self.__slots     = []
        self.dest_matrix = None

        self.window.root.geometry(f'+{pyautogui.position()[0]}+{pyautogui.position()[1]}')

        globals()['interrupted'] = False

        for row in self.__grid:
            row.extend('#' * (self.__w - len(row)))

        self.__slots = self.__find_slots()

        self.window.frame().Label(text=gtbk('compiling'), size=10, row=0, col=0)

        self.progressbar = self.window.frame().Progressbar(
            variable     = None,
            mode         = 'determinate',
            upper        = len(self.__slots) if not testing else 50,
            row          = 1,
            col          = 0,
            widgetkwargs = {
                'length'  : 300,
          }
        )
        CwcButtonTkmt(
            master           = self.window.frame(),
            image_base_name  = 'close',
            command          = self.__finished,
            row              = 2,
            col              = 0,
            sticky           = tk.N,
            pady             = (0,5),
            busy_is_disabled = False
        )

    @staticmethod
    def exclude_word(word, when:ExcludedWhen):
        CrosswordFiller.__excluded_words.append({word : when})

    def run(self, testing=False):
        self.set_word_lists()

        if testing:
            self.window.root.after(200, self.execute_test)
        else:
            self.window.root.after(200, self.execute)

        self.window.show()
        return self.dest_matrix

    def set_word_lists(self):
        self.__load_wordlists()

    def execute(self):
        thread = Thread(target=self.__execute, daemon=True)
        thread.start()

    def execute_test(self):
        thread = Thread(target=self.__execute_test, daemon=True)
        thread.start()

    def __finished(self, matrix=None):
        globals()['interrupted'] = True
        while globals()['RUNNING']:
            time.sleep(0.1)
        self.dest_matrix = matrix
        self.window.quit()

    def __execute(self):
        matrix = []
        sol = self.__solve()
        if sol:
            for row in self.__display_solution(sol):
                row_matrix = []
                for c in row:
                    row_matrix.append(c.replace('.', '_'))
                print(row)
                matrix.append(row_matrix)
        self.__finished(matrix=matrix)

    def __execute_test(self):
        for i in range(50):
            self.progressbar['value'] = i
            self.window.root.update_idletasks()
            time.sleep(0.1)
        self.progressbar.stop()
        self.window.quit()

    def __load_wordlists(self):
        query = f'SELECT value FROM word WHERE LENGTH(value) IN ({self.__lengths_to_str()})'
        if len(CrosswordFiller.__excluded_words) > 0:
            query += ' AND UPPER(value) NOT IN ('

            words_copy = CrosswordFiller.__excluded_words.copy()

            for index, _ in enumerate(words_copy):
                word = next(iter(CrosswordFiller.__excluded_words[index]))
                query += f"'{word}'"
                if index < (len(words_copy) - 1):
                    query += ', '
                if {word : ExcludedWhen.EW_ONCE} in CrosswordFiller.__excluded_words:
                    CrosswordFiller.__excluded_words.remove({word : ExcludedWhen.EW_ONCE})
            query += ')'
        query += ' ORDER BY random()'

        with lock:
            connection = sqlite3.connect(GlobalData.current_db_file(), check_same_thread=False)
            cursor     = connection.cursor()
            cursor.execute(query)

            self.__wordlists = defaultdict(list)  # length -> [word,...]
            for (_w,) in cursor:
                _w = _w.strip().upper()
                self.__wordlists[len(_w)].append(_w)

    def __add_to_lengths(self, length):
        if not length in self.lengths:
            self.lengths.append(length)

    def __lengths_to_str(self):
        return ', '.join(map(str, self.lengths))

    def __find_slots(self):
        slots = []
        name_ctr = defaultdict(int)
        for direction in (Direction.HORIZONTAL, Direction.VERTICAL):
            for y in range(self.__h):
                for x in range(self.__w):
                    if direction == Direction.HORIZONTAL:
                        cond_starts = self.__grid[y][x] != '#' and (x==0 or self.__grid[y][x-1] == '#')
                        length = 1
                        while x+length < self.__w and self.__grid[y][x+length]=='.':
                            length += 1
                        if cond_starts and length>=2:
                            name_ctr['A'] += 1
                            name = f"A{name_ctr['A']}"
                            slots.append(Slot(name, y, x, direction, length, []))
                            self.__add_to_lengths(length=length)
                    else:
                        cond_starts = self.__grid[y][x] != '#' and (y==0 or self.__grid[y-1][x] == '#')
                        length = 1
                        while y + length<self.__h and self.__grid[y + length][x]=='.':
                            length += 1
                        if cond_starts and length>=2:
                            name_ctr['D'] += 1
                            name = f"D{name_ctr['D']}"
                            slots.append(Slot(name, y, x, direction, length, []))
                            self.__add_to_lengths(length=length)

        # compute overlaps
        name2slot = {s.name: s for s in slots}
        pos2slots = defaultdict(list)

        for s in slots:
            for k in range(s.length):
                y = s.y + (k if s.direction == Direction.VERTICAL   else 0)
                x = s.x + (k if s.direction == Direction.HORIZONTAL else 0)
                pos2slots[(y, x)].append( (s.name, k) )
        for key, lst in pos2slots.items():
            if len(lst) == 2:
                (s1,k1),(s2,k2) = lst
                name2slot[s1].overlaps.append((s2, k1, k2))
                name2slot[s2].overlaps.append((s1, k2, k1))
        return slots

    def __solve(self):
        defined_words = get_not_empty_words()

        defined_domains = {
            s.name:
            [
                get_word_by_coord_and_direction((s.y, s.x), s.direction).get_word()
            ]
            for s in self.__slots if ((s.y, s.x), s.direction) in
                [
                    (w.get_coordinates(), w.get_direction()) for w in defined_words
                ]
        }
        free_domains = {
            s.name: self.__filtered_initial(s) for s in self.__slots if ((s.y, s.x), s.direction) not in
            [
                (w.get_coordinates(), w.get_direction()) for w in defined_words
            ]
        }
        domains = dict(defined_domains, **free_domains)
        assignment = {}
        used = set()
        globals()['RUNNING'] = True
        return self.__backtrack(assignment=assignment, domains=domains, used=used)

    def __filtered_initial(self, slot):
        # no fixed letters yet, just length
        return list(set(self.__wordlists.get(slot.length, [])))

    def __backtrack(self, assignment, domains, used):
        if globals()['interrupted']:
            globals()['RUNNING'] = False
            return dict(assignment)

        if len(assignment) == len(self.__slots):
            if self.progressbar:
                self.progressbar.stop()
            globals()['RUNNING'] = False
            return dict(assignment)

        try:
            self.progressbar['value'] = len(assignment) + 1
            self.window.root.update_idletasks()

            # MRV: pick slot not assigned with minimal remaining domain
            unfilled  = [s for s in self.__slots if s.name not in assignment]
            #name2slot = {s.name: s for s in self.__slots}
            slot      = min(unfilled, key=lambda s: len(domains[s.name]))
            slot_name = slot.name

            # If no candidates → fail
            if not domains[slot_name]:
                globals()['RUNNING'] = False
                return None

            for word in list(domains[slot_name]):
                if word in used:
                    continue
                # check consistency with already assigned neighbors
                ok = True
                for (other_name, my_k, other_k) in slot.overlaps:
                    if other_name in assignment:
                        other_word = assignment[other_name]
                        if word[my_k] != other_word[other_k]:
                            ok = False
                            break
                if not ok:
                    continue

                # tentatively assign
                assignment[slot_name] = word
                used.add(word)

                saved_domains = {}
                forward_ok    = True

                # forward-check neighbors
                for (other_name, my_k, other_k) in slot.overlaps:
                    if other_name in assignment:
                        continue
                    saved_domains[other_name] = domains[other_name]
                    filtered = [w2 for w2 in domains[other_name] if w2[other_k] == word[my_k]]
                    if not filtered:
                        forward_ok = False
                        break
                    domains[other_name] = filtered

                if forward_ok:
                    sol = self.__backtrack(assignment=assignment, domains=domains, used=used)
                    if sol:
                        return sol

                # undo
                for k in saved_domains:
                    domains[k] = saved_domains[k]
                assignment.pop(slot_name)
                used.remove(word)
        except Exception as e:
            print(e)

        globals()['RUNNING'] = False
        return None

    def __display_solution(self, sol):
        sol_grid = [row.copy() for row in self.__grid]
        name2slot = {s.name: s for s in self.__slots}
        for name, word in sol.items():
            s = name2slot[name]
            for k, ch in enumerate(word):
                y = s.y + (k if s.direction==Direction.VERTICAL   else 0)
                x = s.x + (k if s.direction==Direction.HORIZONTAL else 0)
                sol_grid[y][x] = ch
        return [''.join(row) for row in sol_grid]


############# TESTS #############

if __name__ == '__main__':
    from cwc_style import set_style

    set_style()

    _grid = [
      "#....##....",
      "#..#...#.#.",
      "#..##..#...",
      "#......#...",
      "##.##.##..."
    ]
    # Tests only the progressbar
    _filler = CrosswordFiller(grid=_grid, bind_esc=True)
    CrosswordFiller.exclude_word(word='CIAO', when=ExcludedWhen.EW_ALWAYS)
    CrosswordFiller.exclude_word(word='AAAA', when=ExcludedWhen.EW_ONCE)
    CrosswordFiller.exclude_word(word='BBBB', when=ExcludedWhen.EW_ONCE)
    _filler.run(testing=True)
