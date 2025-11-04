"""Module to handle the words"""

import json

from cwc_globals import (
    GlobalData,
    Direction
)
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)

class Word:
    """Class to handle the words of the app"""

    index = 1

    def __init__(
        self,
        coordinates:tuple,
        length:int,
        direction:Direction,
        all_coordinates:list = None,
        index:int            = -1,
        word:str             = None,
        name:str             = None,
        definitions:list     = None
    ):
        self.coordinates        = coordinates
        self.length             = length
        self.direction          = direction
        self.all_coordinates    = all_coordinates if all_coordinates else []
        self.index              = index if index >= 0 else Word.index
        self.word               = word if word else ''.ljust(length, '_')
        self.name               = name if name else f'word_{Word.index}'
        self.definitions        = definitions if definitions else []
        self.current_definition = None

        self.set_all_coordinates()

        Word.index += 1

    def to_json(self):
        """Needed by jsonpickle used in class Project"""

        return json.dumps(
            self,
            default   = lambda o: o.__dict__,
            sort_keys = True,
            indent    = 3
        )

    def __del__(self):
        try:
            Word.index = 1
        except Exception as e:
            print(e)

    def get_name(self):
        return self.name

    def get_y(self):
        return self.coordinates[0]

    def get_x(self):
        return self.coordinates[1]

    def get_length(self):
        return self.length

    def get_direction(self):
        return self.direction

    def get_word(self):
        return self.word

    def is_empty(self):
        return '_' in self.word

    def get_coordinates(self):
        return self.coordinates

    def get_all_coordinates(self):
        return self.all_coordinates

    def add_definition(self, definition):
        self.definitions.append(definition)

    def get_definitions(self):
        return self.definitions

    def clear_definitions(self):
        self.definitions.clear()

    def set_current_definition(self, index=None, definition=None):
        if index is not None:
            self.current_definition = index
        elif definition:
            try:
                self.current_definition = self.definitions.index(definition)
            except ValueError:
                self.current_definition = None

    def get_current_definition(self):
        if self.current_definition is not None and len(self.definitions) > self.current_definition:
            return self.definitions[self.current_definition]
        return None

    def set_all_coordinates(self):
        """Sets all the matrix coordinates used by the word.
        This makes it easier and faster to handle the interaction with other words.
        """
        self.all_coordinates.append(self.get_coordinates())

        for i in range(1, self.length):
            if self.direction == Direction.HORIZONTAL:
                self.all_coordinates.append((self.get_y(), self.get_x() + i))
            else:
                self.all_coordinates.append((self.get_y() + i, self.get_x()))

    def set_char_to_word(self, y, x, char):
        """If Y and X are coordinates of the word, it sets the CHAR to those cooordinates.
        Since the matrix has been changed, it looks for all words that might have been changed
        and, in case, emits a signal.
        Signals are:
            - emit_full_word_set: a word has all chars set
            - emit_word_emptied: a previously full word has been emptied (1 char set to '' is enough).
        To achieve this, it first looks for all empty and not empty words and, after the char being set,
        checks for the differencies.
        """
        try:
            if (y, x) in self.all_coordinates:
                _empty_words    = get_empty_words    () # gets all not empty words to see later if more
                not_empty_words = get_not_empty_words() # gets all empty words to see later if more
                CwcMatrix.set_variable_value(y=y, x=x, value='' if char == '_' else char)
                str_copy = self.word
                list_str = list(str_copy)

                if self.direction == Direction.HORIZONTAL:
                    list_str[x - self.coordinates[1]] = char
                else:
                    list_str[y - self.coordinates[0]] = char

                word_copy = self.word[:]

                self.word = ''.join(list_str)

                full_words = set(_empty_words) - set(get_empty_words())
                for w in full_words: # if more empty words, informs
                    Word.emit_full_word_set(word=w)

                emptied_words = set(not_empty_words) - set(get_not_empty_words())
                for w in emptied_words: # if more empty words, informs
                    Word.emit_word_emptied(word=w)

                for w in not_empty_words: # current word might have been changed
                    if self == w and self.get_word() != word_copy:
                        Word.emit_full_word_set(word=self)
                        break
        except Exception as e:
            print(e)

    def set_word(self, letters):
        """Sets all the LETTERS of the word."""

        print(f'setting word {letters} to word {self.get_name()} - {self.get_coordinates()} - {self.get_direction}')

        x = self.get_x()
        y = self.get_y()

        for c in letters:
            set_char_to_words(y=y, x=x, char=c)
            if self.get_direction() == Direction.HORIZONTAL:
                x += 1
            else:
                y += 1

        if self.is_empty():
            Word.emit_word_emptied(word=self)

    def clear(self):
        """Clears the letters and the definitions of the word."""
        self.word = ''.ljust(self.length, '_')
        self.current_definition = None
        self.clear_definitions()

##################################################################

def get_word_by_name(name):
    for w in GlobalData.words:
        if w.get_name() == name:
            return w
    return None

def get_words_by_coord(coord)->list[Word]:
    words = []
    for w in GlobalData.words:
        if coord == w.get_coordinates():
            words.append(w)
    return words

def get_word_by_coord_and_direction(coord, direction):
    for w in GlobalData.words:
        if coord == w.get_coordinates() and direction == w.get_direction():
            return w
    return None

def get_words_by_all_coord(coord, exclude_word=None, only_not_empty=False):
    return [
        w for w in GlobalData.words if
            coord in w.get_all_coordinates() and
            w != exclude_word                and
            (
                only_not_empty is False or not w.is_empty()
            )
        ]

def create_word_from_json(js:str):
    """Create a word from a json string JS.
    Used when save/open the crossword.
    """
    try:
        data            = json.loads(js)
        coordinates     = tuple(data['coordinates']['py/tuple'])
        length          = data['length']
        direction       = get_direction(data=data)
        all_coordinates = get_all_coordinates(data=data)
        word            = data['word']
        name            = data['name']
        definitions     = data['definitions']
        index           = data['index']
        w = Word(
            coordinates     = coordinates,
            length          = length,
            direction       = direction,
            all_coordinates = all_coordinates,
            word            = word,
            name            = name,
            definitions     = definitions,
            index           = index
        )
        return w
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def get_all_coordinates(data):
    all_coordinates = []
    try:
        coordinates = data['all_coordinates']

        for coord in coordinates:
            all_coordinates.append(tuple(coord['py/tuple']))
    except Exception as e:
        print(f"KeyError: {e}")

    return all_coordinates

def get_direction(data):
    try:
        direction       = Direction(data['direction']['py/reduce'][1]['py/tuple'][0]['py/tuple'][0])
    except Exception as e:
        direction       = Direction(data['direction']['py/reduce'][1]['py/tuple'][0])
    return direction

def set_char_to_words(y, x, char):
    # TODO: very expensive, find a better way
    try:
        for w in get_words_by_all_coord(coord=(y, x)):
            w.set_char_to_word(y=y, x=x, char=char)
    except Exception as e:
        print(e)

def del_char_from_words(y, x):
    set_char_to_words(y=y, x=x, char='_')

def del_chars_not_used_by_other_words(word):
    y = word.get_y()
    x = word.get_x()

    for c in word.get_word():
        words = get_words_by_all_coord(coord=(y, x), exclude_word=word, only_not_empty=True)
        if not words:
            set_char_to_words(y=y, x=x, char='_')

        if word.get_direction() == Direction.HORIZONTAL:
            x += 1
        else:
            y += 1

def clear_word(word):
    word.clear_definitions()
    word.set_current_definition(None)
    word.set_word(letters=''.ljust(word.get_length(), '_'))

def get_cell_by_word(word):
    for y in range(GlobalData.TOT_ROWS):
        for x in range(GlobalData.TOT_COLS):
            cell = CwcMatrix.get(matrix_type=MatrixType.ENTRY, y=y, x=x)
            if cell and word in cell.words():
                return cell
    return None

def get_not_empty_words():
    return [w for w in GlobalData.words if not w.is_empty()]

def get_empty_words():
    return [w for w in GlobalData.words if w.is_empty()]

def empty_words():
    for w in GlobalData.words:
        w.clear()


############# TESTS #############

if __name__ == "__main__":
    pass # TODO
