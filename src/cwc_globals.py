"""This code is based on TKinterModernThemes (c) RobertJN64, MIT License.
See LICENSE for details - https://github.com/RobertJN64/TKinterModernThemes.
----

This code is based on CustomTkinter (c) Tom Schimansky, MIT License.
See LICENSE for details - https://github.com/TomSchimansky/CustomTkinter
----

Module to define global data for the application """

import os
import csv
import json
from enum import Enum

from dataclasses import dataclass

import tkinter as tk

import pyautogui

from babel import Locale, localedata

from PIL import Image, ImageGrab

from TKinterModernThemes import ThemedTKinterFrame as TKMT
from customtkinter       import CTkImage

if '_internal' in os.path.dirname(__file__):
    __ROOT_DIR = os.path.dirname(__file__)
else:
    __ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')

print(f'###########: {__ROOT_DIR}')

__CONFIG_DIR            = os.path.join(__ROOT_DIR, 'config')
__SETTINGS_FILENAME     = os.path.join(__ROOT_DIR, __CONFIG_DIR, 'cwc_settings.json')
__TRANSLATIONS_FILENAME = os.path.join(__ROOT_DIR, __CONFIG_DIR, 'translatable_text.json')
__FORBID_CURS           = ''


class Direction(Enum):
    """Defines the word's direction."""

    NONE       = -1
    VERTICAL   = 0
    HORIZONTAL = 1

class AppState(Enum):
    """Defines the application's state."""

    AS_NONE           = -1
    AS_CW_NOT_CREATED = 0
    AS_CW_CREATED     = 1
    AS_CW_FINALIZED   = 2
    AS_CW_FILLED      = 3
    AS_CW_COMPLETE    = 4
    AS_BUSY           = 5

@dataclass
class Theme:
    """Defines the application's theme."""

    APP_THEMES = [
        'azure',
        'sun-valley',
        'park'
    ]
    APP_MODES = [
        'light',
        'dark'
    ]

    CURRENT_APP_THEME = 'park'
    CURRENT_APP_MODE  = 'dark'

# loads all translatable texts
with open(__TRANSLATIONS_FILENAME, 'r', encoding='utf-8') as json_file:
    all_translatable_texts = json.load(json_file)

def get_translation_by_key(key, lang):
    try:
        return next(d[lang] for d in all_translatable_texts[key] if lang in d)
    except Exception as e:
        return '?'

def get_key_by_value(value, lang):
    try:
        for key in all_translatable_texts:
            v = get_translation_by_key(key=key, lang=lang)
            if v == value:
                return key
    except Exception as e:
        print(e)
    return '?'

def get_settings(saved=True):
    with open(__SETTINGS_FILENAME, 'r', encoding='latin-1') as f:
        settings = json.load(f)

    if saved:
        return settings

    settings['definitions']['hide_sel'] = GlobalData.CH_HIDE_VAR.get()
    settings['definitions']['auto_sel'] = GlobalData.CH_AUTO_SEL.get()
    settings['appearance' ]['theme'   ] = Theme.CURRENT_APP_THEME
    settings['appearance' ]['mode'    ] = Theme.CURRENT_APP_MODE
    return settings

def get_setting(keys):
    settings = get_settings()
    for key in keys:
        settings = settings[key]
    return settings

def save_settings(settings):
    with open(__SETTINGS_FILENAME, 'w', encoding='latin-1') as f:
        json.dump(obj=settings, fp=f, indent=3)

class App(TKMT):
    """The application."""

    def __init__(self):
        Theme.CURRENT_APP_THEME = get_setting(['appearance', 'theme'])
        Theme.CURRENT_APP_MODE  = get_setting(['appearance', 'mode' ])

        super().__init__(title="CWC", theme=Theme.CURRENT_APP_THEME, mode=Theme.CURRENT_APP_MODE)

@dataclass
class GlobalData:
    """Data used by all modules."""

    main_tkmt_window = App()
    main_window      = main_tkmt_window.root

    CURRENT_LANGUAGE         = 'it'
    CURRENT_ARCHIVE_LANGUAGE = 'it'

    CH_HIDE_VAR               = tk.BooleanVar(value=True)
    CH_AUTO_SEL               = tk.BooleanVar(value=True)
    FIND_DEFS                 = tk.StringVar (value='')
    SKIP_BLACK_CELLS          = tk.BooleanVar(value=True)
    AUTO_MOVE                 = tk.BooleanVar(value=True)
    THEME_VAR                 = tk.StringVar()
    APPEARENCE_VAR            = tk.StringVar()
    TOOLTIP_OPEN_TIME_MS      = 1.0
    TOOLTIP_CLOSE_TIME_MS     = 3.0
    MAX_CONTIGOUS_BLACK_CELLS = 4
    RESIZE_MAX_VALUE          = 20
    RESIZE_MIN_VALUE          = 2
    TOT_ROWS                  = 6
    TOT_COLS                  = 6
    BLACK_PERCENT             = 5
    CURRENT_FONT_SIZE         = 16
    CURRENT_FONT_NAME         = 'Helvetica'
    CURRENT_SCALE_VALUE       = RESIZE_MIN_VALUE
    WINDOW_STATE              = 'normal'

    CURRENT_AUTOMOVE_DIRECTION = None
    __CURRENT_STATE            = AppState.AS_CW_NOT_CREATED
    OPEN_CW_APP_STATE          = AppState.AS_CW_NOT_CREATED

    MIN_MAX_DIMENSIONS         = (4 , 20)
    MIN_MAX_TMPL_DIMENSIONS    = (2 , 6 )
    MIN_MAX_TMPL_REPEAT        = (0 , 6 )
    MIN_MAX_BLACK_CELLS_AMOUNT = (1 , 10)
    MIN_MAX_FONT_DIMENSIONS    = (10, 30)
    MIN_MAX_WORD_LENGTH        = (4 , 30)
    MAX_WORD_LENGTH            = 4
    HORIZ_ARROW                = '→'
    VERT_ARROW                 = '↓'
    LEFT_DOUBLE_ARROW          = '⇦'
    RIGHT_DOUBLE_ARROW         = '⇨'
    DOWN_RIGHT_ARROW           = '↳ '
    UP_JOIN_ARROW              = '╖'
    DOWN_JOIN_ARROW            = '╜'
    DOUBLE_VERTICAL            = '║'
    DOUBLE_HORIZONTAL          = '═'
    ROOT_DIR                   = globals()['__ROOT_DIR']
    TEMPLATE_DIR               = 'templates'
    PLUGINS_DIR                = 'plugins'
    CONFIG_DIR                 = globals()['__CONFIG_DIR']
    IMAGES_DIR                 = 'images'
    DB_DIR                     = 'db'
    __DB_FILE                  = os.path.join(ROOT_DIR, DB_DIR, CURRENT_ARCHIVE_LANGUAGE, 'cwc.db')
    ICO_FILENAME               = os.path.join(ROOT_DIR, IMAGES_DIR  , 'cwc.ico')
    SEARCH_ENGINES_FILENAME    = os.path.join(ROOT_DIR, CONFIG_DIR  , 'search_engines.csv')
    TEMPLATES_FILENAME         = os.path.join(ROOT_DIR, TEMPLATE_DIR, 'templates.json')
    SETTINGS_FILENAME          = globals()['__SETTINGS_FILENAME']
    TITLE_FONT                 = (CURRENT_FONT_NAME, 12, 'bold')
    VALUE_FONT                 = (CURRENT_FONT_NAME, 10, 'normal')
    VALUE_FONT_BOLD            = (CURRENT_FONT_NAME, 9 , 'bold')
    MAIN_BUTTON_FONT           = (CURRENT_FONT_NAME, 8 , 'bold')
    SMALL_FONT                 = ('arial', 8 , 'normal')
    SMALL_COMBO_FONT           = 'Verdana 8'
    EXPORTER_FONT_NAME         = 'arial'
    FONT_SMALL_SIZE            = 10
    FONT_BIG_SIZE              = 22
    SETTING_THEME              = False # used to enable/disable auto call CWC.__set_appearence on theme change
    BLOCK_SIGNALS              = False # used to block calls on all trace tk variables

    # Margin for the popup_menu
    # A transparent frame with a margin is used to avoid the popup menu to be closed when the mouse
    # leaves the menu area. This is useful to keep the menu open while the user is moving the mouse
    # to select an option
    POPUP_MENU_WINDOW_MARGIN = 40
    ###############################

    words = []

    @staticmethod
    def current_state():
        return GlobalData.__CURRENT_STATE

    @staticmethod
    def set_current_state(state:AppState):
        """Set state to STATE and emits a not implemented method 'emit_state_changed'
        that has to be bound
        """
        if state != AppState.AS_NONE:
            GlobalData.__CURRENT_STATE = state
            print(f'State set to "{state.name}"')
            GlobalData.emit_state_changed()

    @staticmethod
    def current_db_file():
        GlobalData.__DB_FILE = os.path.join(
            GlobalData.ROOT_DIR,
            GlobalData.DB_DIR,
            GlobalData.CURRENT_ARCHIVE_LANGUAGE,
            'cwc.db'
        )
        return GlobalData.__DB_FILE

class Colors:
    """Defines the application's colors."""

    white             = '#FFFFFF'
    black             = '#000000'
    blue              = '#2e54ff'
    red               = "#FF0000"
    light_blue        = "#7FC0FD"
    very_light_blue   = "#9ADAFF"
    light_green       = "#78FF83"
    dark_green        = '#23992D'
    light_red         = "#FF705B"
    dark_red          = '#A54F42'
    yellow            = "#FFF67A"
    orange            = "#FFB617"
    button_fg         = "#AC9E81"
    light_yellow      = "#FFF898"
    very_light_yellow = "#FFFBCA"
    dark_yellow       = "#CCBF06"
    dark_grey         = "#363636"
    dark_grey2        = "#555353"
    grey              = "#727272"
    light_grey        = "#CDC6C6"
    very_light_grey   = "#E6E1E1"
    bg_descr_label    = "#CCB189"
    bg_msg_label      = "#FDFFEF"
    highlight_btn     = "#EBB1B1"
    cwc_button_border = "#A16A6A"
    cwc_separator     = "#A58A8A"
    cwc_toplevel      = "#C9A7A7"
    label_frame_col   = None

def clear_words():
    GlobalData.words.clear()

def clear_all():
    clear_words()

def get_matrix_dimensions(key):
    """Return the size of the element KEY based on the GlobalData.CURRENT_FONT_SIZE"""

    match key:
        case 'white_frame' : return int(GlobalData.CURRENT_FONT_SIZE) * 3
        case 'black_frame' : return get_matrix_dimensions('white_frame') - 4
        case 'white_font'  : return int(GlobalData.CURRENT_FONT_SIZE)
        case 'number_font' : return max(6, int(GlobalData.CURRENT_FONT_SIZE // 2))

def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """

    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method

def unbind(instance, as_name):
    delattr(instance, as_name)

def get_empty_words_coordinates():
    """Return a sorted json list of empty words' coordinates."""

    w_coords = [ {'w' : w, 'c' : w.get_coordinates()} for w in GlobalData.words if w.is_empty()]
    w_coords = sorted(w_coords, key=lambda d: d['c'])
    return w_coords

def get_parent_widget(widget, level=1):
    """Return the parent of the widget going up to level LEVEL."""

    try:
        for i in range(level):
            parent_name = widget.winfo_parent()
            widget = widget.nametowidget(parent_name)
        return widget
    except Exception as e:
        print(e)
    return None

def center_window(win, to_screen=False):
    win.attributes('-alpha', 0)
    win.update_idletasks()

    width  = win.winfo_width()
    height = win.winfo_height()
    if to_screen:
        x = (win.winfo_screenwidth () // 2) - (width  // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
    else:
        x = GlobalData.main_window.winfo_x() + (GlobalData.main_window.winfo_width()  - width ) // 2
        y = GlobalData.main_window.winfo_y() + (GlobalData.main_window.winfo_height() - height) // 2
    win.geometry(f'+{x}+{y}')

    win.attributes('-alpha', 1)

def set_window_to_mouse_point(win:tk.Toplevel, modify_x=0, modify_y=0, margin=False):
    win.attributes('-alpha', 0)

    win.update_idletasks()

    x = pyautogui.position()[0]

    if margin:
        x -= GlobalData.POPUP_MENU_WINDOW_MARGIN

    y = pyautogui.position()[1]
    if margin:
        y -= GlobalData.POPUP_MENU_WINDOW_MARGIN

    if modify_x:
        x += modify_x
    if modify_y:
        y += modify_y

    # reduce coordinates if the win would exceed the screen size
    if (x + win.winfo_width()) > win.winfo_screenwidth():
        x -= ((x + win.winfo_width()) - win.winfo_screenwidth())

    if (y + win.winfo_height()) > (win.winfo_screenheight() - 50):
        y -= ((y + win.winfo_height()) - win.winfo_screenheight() + 50) # 50 for the taskbar's height

    win.geometry(f'+{x}+{y}')
    win.attributes('-alpha', 1)

def set_window_to_mouse_point_tk(win:tk.Toplevel):
    try:
        win.update_idletasks()

        x = pyautogui.position()[0]
        x -= GlobalData.POPUP_MENU_WINDOW_MARGIN

        y = pyautogui.position()[1]
        y -= GlobalData.POPUP_MENU_WINDOW_MARGIN

        # reduce coordinates if the win would exceed the screen size
        if (x + win.winfo_width()) > win.winfo_screenwidth():
            x -= ((x + win.winfo_width()) - win.winfo_screenwidth())

        if (y + win.winfo_height()) > (win.winfo_screenheight() - 50):
            y -= ((y + win.winfo_height()) - win.winfo_screenheight() + 50) # 50 for the taskbar's height

        win.geometry(f'+{x}+{y}')
    except Exception as e:
        print(e)

def get_black_cells_type(type_id):
    match type_id:
        case 0:
            return 'random'
        case 1:
            return 'manual'
        case 2:
            return 'template'

def get_black_cells_type_id(type_name):
    match type_name:
        case 'random':
            return 0
        case 'manual':
            return 1
        case 'template':
            return 2

def get_search_defs_url():
    settings = get_settings()

    engine    = settings['definitions']['search_engine']
    add_words = settings['definitions']['add_words'    ]

    with open(GlobalData.SEARCH_ENGINES_FILENAME, 'r', encoding='latin-1') as csvfile:
        r = csv.reader(csvfile, delimiter=';')
        value = [row[1] for row in r if row[0] == engine]
        if len(value) > 0:
            return value[0] + ' ' + add_words
    return ''

def all_children(frame, find_list=None, widget_names=None):
    children = frame.winfo_children()
    for item in children:
        if widget_names is None or item.widgetName in widget_names:
            find_list.append(item)
        all_children(item, find_list, widget_names=widget_names)

def get_internal_image(base_name, size=20):
    return CTkImage(
        light_image          = Image.open(os.path.join(GlobalData.ROOT_DIR, f'images/{base_name}.png')),
        dark_image           = Image.open(os.path.join(GlobalData.ROOT_DIR, f'images/{base_name}.png')),
        light_image_disabled = Image.open(os.path.join(GlobalData.ROOT_DIR, f'images/{base_name}-disabled.png')),
        dark_image_disabled  = Image.open(os.path.join(GlobalData.ROOT_DIR, f'images/{base_name}-disabled.png')),
        size                 = (size, size)
)

def get_image(path, size=20):
    return CTkImage(
        light_image = Image.open(path),
        size        = (size, size)
)

def get_language_code(language):
    for lid in localedata.locale_identifiers():
        loc = Locale.parse(lid)
        if str(loc.display_name).lower() == language.lower():
            return loc.language
    return None

def get_language(code:str):
    try:
        locale     = code
        locale_obj = Locale(locale)
        return str(locale_obj.display_name).split(sep='(', maxsplit=1)[0].strip().capitalize()
    except Exception as e:
        print(e)
        return 'it' # defaults to italian

def change_language(language):
    widgets = []
    all_children(frame=GlobalData.main_window, find_list=widgets)
    for w in widgets:
        try:
            text = str(w['text'])
            if text.startswith(GlobalData.DOWN_RIGHT_ARROW):
                _text = text[len(GlobalData.DOWN_RIGHT_ARROW):]
            else:
                _text = text
            key = get_key_by_value(value=_text.strip(), lang=GlobalData.CURRENT_LANGUAGE)
            if key != '?':
                if text.startswith(GlobalData.DOWN_RIGHT_ARROW):
                    w.configure(text=GlobalData.DOWN_RIGHT_ARROW + get_translation_by_key(key=key, lang=language))
                elif text.startswith(' ') and text.endswith(' '):
                    w.configure(text=f' {get_translation_by_key(key=key, lang=language)} ')
                else:
                    w.configure(text=get_translation_by_key(key=key, lang=language))
        except Exception:
            pass

    if hasattr(GlobalData, 'emit_change_language') and callable(getattr(GlobalData, 'emit_change_language')):
        GlobalData.emit_change_language(language=language)

    GlobalData.CURRENT_LANGUAGE = language

def set_app_settings(settings=None, set_language=False):
    if not settings:
        settings = get_settings()

    GlobalData.BLOCK_SIGNALS = True
    GlobalData.CH_HIDE_VAR     .set(settings['definitions']['hide_sel'     ])
    GlobalData.CH_AUTO_SEL     .set(settings['definitions']['auto_sel'     ])
    GlobalData.SKIP_BLACK_CELLS.set(settings['word_editing']['skip_black'])
    GlobalData.AUTO_MOVE       .set(settings['word_editing']['auto_move'])
    GlobalData.FIND_DEFS       .set(settings['definitions']['search_engine'])

    if set_language:
        change_language(language=settings['appearance']['language'])
    else:
        GlobalData.CURRENT_LANGUAGE = settings['appearance']['language']

    theme = settings['appearance']['theme']
    mode  = settings['appearance']['mode']
    if theme != Theme.CURRENT_APP_THEME or mode != Theme.CURRENT_APP_MODE:
        GlobalData.SETTING_THEME = True
        Theme.CURRENT_APP_THEME = settings['appearance']['theme']
        Theme.CURRENT_APP_MODE  = settings['appearance']['mode']
        GlobalData.THEME_VAR     .set(Theme.CURRENT_APP_THEME)
        GlobalData.APPEARENCE_VAR.set(Theme.CURRENT_APP_MODE)
        GlobalData.SETTING_THEME = False

    GlobalData.BLOCK_SIGNALS = False

def save_frame_as_image(frame, filename):
    x      = frame.winfo_rootx()
    y      = frame.winfo_rooty()
    width  = frame.winfo_width()
    height = frame.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    img.save(filename)

def get_forbid_curs():
    """When running from pyinstaller, images will be in _internal/images and
    for the cursor this appears to be a problem. So, at the first call,
    try to configure a label with a cursor. If it fails, sets the path with "_internal"
    """
    if globals()['__FORBID_CURS'] == '':
        try:
            tk.Label(cursor='@images/forbid.cur')
            globals()['__FORBID_CURS'] = '@images/forbid.cur'
        except Exception:
            globals()['__FORBID_CURS'] = '@_internal/images/forbid.cur'
    return globals()['__FORBID_CURS']

############# TESTS #############

if __name__ == "__main__":
    # does nothing, just check if errors raise
    GlobalData.main_window.mainloop()
