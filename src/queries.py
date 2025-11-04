"""All the db queries"""

GET_WORDS_BY_LIKE_QUERY = """SELECT UPPER(value) FROM word WHERE LOWER(value) LIKE LOWER('{like}') ORDER BY 1
"""

GET_DEFINITIONS_QUERY = """SELECT
    UPPER(w.value) AS key,
    d.value        AS value
FROM
            word_definition wd
INNER JOIN  word            w  ON w.id = wd.word_id
INNER JOIN  definition      d  ON d.id = wd.definition_id
WHERE
    UPPER(w.value) = '{word}'
ORDER BY d.value
"""

GET_DEFINITIONS_MULTIPLE_WORDS_QUERY = """SELECT
    UPPER(w.value) AS key,
    d.value        AS value
FROM
            word_definition wd
INNER JOIN  word            w  ON w.id = wd.word_id
INNER JOIN  definition      d  ON d.id = wd.definition_id
WHERE
    UPPER(w.value) IN ({words})
ORDER BY d.value
"""

INSERT_WORD_DEFINTION_IDS_QUERY = """INSERT INTO word_definition (word_id, definition_id) VALUES (
    (SELECT id FROM word WHERE UPPER(value) = UPPER('{word}')),
    {definition_id}
)
"""

DELETE_WORD_QUERY = """DELETE FROM word WHERE UPPER(value) = UPPER('{word}')
"""

DELETE_DEFINITION_QUERY = """DELETE FROM definition WHERE UPPER(value) = UPPER('{definition}')
"""

INSERT_WORD_QUERY = """INSERT INTO word (value) VALUES ('{word}') RETURNING ID
"""

INSERT_DEFINITION_QUERY = """INSERT INTO definition (value) VALUES ('{definition}') RETURNING ID
"""

UPDATE_DEFINITION_QUERY = """UPDATE definition SET value = '{new_definition}' WHERE UPPER(value) = UPPER('{old_definition}')
"""

WORD_EXISTS_QUERY = """SELECT 1 FROM word WHERE UPPER(value) = UPPER('{word}')
"""
