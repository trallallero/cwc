import sqlite3
from cwc_globals import GlobalData

from queries import (
    GET_WORDS_BY_LIKE_QUERY,
    GET_DEFINITIONS_QUERY,
    GET_DEFINITIONS_MULTIPLE_WORDS_QUERY,
    INSERT_DEFINITION_QUERY,
    INSERT_WORD_DEFINTION_IDS_QUERY,
    INSERT_WORD_QUERY,
    DELETE_WORD_QUERY,
    DELETE_DEFINITION_QUERY,
    UPDATE_DEFINITION_QUERY,
    WORD_EXISTS_QUERY
)

class DbConnection():
    def get_words_by_like(self, like):
        _, cursor = self.create_connection()

        q = GET_WORDS_BY_LIKE_QUERY.format(like=like)
        cursor.execute(q)
        vals = cursor.fetchall()
        return [w[0] for w in vals]

    def get_words_by_query(self, query):
        _, cursor = self.create_connection()

        cursor.execute(query)
        vals = cursor.fetchall()
        return [w[0] for w in vals]

    def add_definitions(self, word, definitions:list[str]):
        connection, cursor = self.create_connection()

        for definition in definitions:
            #print(f'Adding definition "{definition}" to word "{word}"')

            q = INSERT_DEFINITION_QUERY.format(definition=definition.replace("'", "''"))
            try:
                cursor.execute(q)

                definition_id = cursor.fetchone()[0]

                q = INSERT_WORD_DEFINTION_IDS_QUERY.format(word=word, definition_id=definition_id)
                cursor.execute(q)
                connection.commit()
            except sqlite3.Error as er:
                print(er)
                connection.rollback()
                return False
        return True

    def get_definitions(self, word):
        _, cursor = self.create_connection()

        q = GET_DEFINITIONS_QUERY.format(word=word)
        #print(q)
        cursor.execute(q)
        vals = cursor.fetchall()
        return [val[1] for val in vals]

    def get_definitions_multiple_words(self, words):
        _, cursor = self.create_connection()

        q = GET_DEFINITIONS_MULTIPLE_WORDS_QUERY.format(words=words)
        #print(q)
        cursor.execute(q)
        vals = cursor.fetchall()
        return vals

    def set_words_definitions(self):
        for w in GlobalData.words:
            w.clear_definitions()

        words_map = {}
        for w in GlobalData.words:
            _word = w.get_word()
            words_map[_word] = w

        words_query = "'" + "', '".join([w.get_word() for w in GlobalData.words]) + "'"
        vals = self.get_definitions_multiple_words(words=words_query)
        for v in vals:
            words_map[v[0]].add_definition(v[1])
            GlobalData.main_window.update()

    def word_exists(self, word):
        _, cursor = self.create_connection()

        q = WORD_EXISTS_QUERY.format(word=word)
        #print(q)
        cursor.execute(q)
        vals = cursor.fetchall()
        return len(vals) > 0 and vals[0][0] == 1

    def add_word(self, word):
        try:
            connection, cursor = self.create_connection()

            q = INSERT_WORD_QUERY.format(word=word)
            cursor.execute(q)
            cursor.fetchall()
            connection.commit()
            return True
        except Exception as e:
            print(e)
            connection.rollback()
        return False

    def remove_word(self, word):
        try:
            connection, cursor = self.create_connection()

            q = DELETE_WORD_QUERY.format(word=word)
            cursor.execute(q)
            connection.commit()
            return True
        except Exception as e:
            print(e)
            connection.rollback()
        return False

    def remove_definition(self, definition):
        try:
            connection, cursor = self.create_connection()

            q = DELETE_DEFINITION_QUERY.format(definition=definition)
            cursor.execute(q)
            connection.commit()
            return True
        except Exception as e:
            print(e)
            connection.rollback()
        return False

    def update_definition(self, old_definition:str, new_definition:str):
        try:
            connection, cursor = self.create_connection()

            q = UPDATE_DEFINITION_QUERY.format(
                old_definition = old_definition.replace("'", "''"),
                new_definition = new_definition.replace("'", "''")
            )
            cursor.execute(q)
            connection.commit()
            return True
        except Exception as e:
            print(e)
            connection.rollback()
        return False

    def create_connection(self):
        connection = sqlite3.connect(GlobalData.current_db_file(), check_same_thread=False)
        cursor     = connection.cursor()
        return connection, cursor


################# TESTS ##################

if __name__ == "__main__":
    _words = DbConnection().get_words_by_like(like='TEST')
    for _w in _words:
        print(_w)

    defs = DbConnection().get_definitions(word='TEST')
    for d in defs:
        print(d)
