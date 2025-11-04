"""Module to find translated texts"""

from cwc_globals import (
    GlobalData,
    all_translatable_texts,
    get_language,
    get_language_code,
    get_translation_by_key,
    get_key_by_value
)

def get_languages():
    """Return all languages found in the cwc_globals._TRANSLATIONS_FILENAME.
    From the first key, looks for the json keys that are the short language codes and
    converts them to long language names.
    Example "it" and "en" -> :
        "find_word" : [
            {"it" : "Cerca parola"},
            {"en" : "Find word"}
        ]
    """

    try:
        for key in all_translatable_texts:
            vals = all_translatable_texts[key]
            languages = []
            for val in vals:
                languages.append(get_language(code=str(list(val.keys())[0])))
            return languages
    except Exception as e:
        print(e)
        return '?'

def gtbk(key):
    """Short way to get a translation value using the current language."""
    return get_translation_by_key(key=key, lang=GlobalData.CURRENT_LANGUAGE)

def gkbv(value):
    """Short way to get a translation key using the current language."""
    return get_key_by_value(value=value, lang=GlobalData.CURRENT_LANGUAGE)


############# TESTS #############

if __name__ == "__main__":
    c = get_language_code(language='english')

    ll = get_languages()

    _VALUE = get_translation_by_key(lang='en', key='del_word')
    assert _VALUE=='Delete word'

    _VALUE = get_translation_by_key(lang='it', key='del_word')
    assert _VALUE=='Cancella parola'

    _VALUE = get_translation_by_key(lang='en', key='sdfsdfsdf')
    assert _VALUE == '?'

    _KEY = get_key_by_value(lang='it', value='Cancella parola')
    assert _KEY == 'del_word'

    _KEY = get_key_by_value(lang='en', value='Delete word')
    assert _KEY == 'del_word'

    _KEY = get_key_by_value(lang='it', value='ghjghjghj')
    assert _KEY == '?'
