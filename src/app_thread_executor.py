""" Module to execute long running methods in a separate thread while showing
a busy cursor and optional cancel button.
"""

import tkinter as tk
from threading import Thread
from time import sleep

from cwc_globals      import (
    GlobalData,
    AppState,
    bind
)
from cwc_toplevel     import CwcTopLevel
from cwc_button       import CwcButtonTkmt
from volatile_message import VolatileMessage
from translations     import gtbk

class AppThreadExecutor(CwcTopLevel):
    """ Class to execute long running methods in a separate thread while showing a busy cursor
    and optional cancel button.
    """

    running = False

    def __init__(
            self,
            result_state:AppState = None,
            show_cancel           = True,
            method                = None,
            message_key           = '',
            send_emits            = True,
            **kwargs
        ):
        """
        RESULT_STATE: the state that will be set when finished. If none, state will be restored
        SHOW_CANCEL : if a 'cancel' buttons should be visible.
        METHOD      : the method to be ran in the thread.
        MESSAGE_KEY : the text's key to be shown.
        SEND_EMITS  : if the emits ('emit_started', 'emit_finished') should be called
        """

        super().__init__(
            title        = '',
            create_frame = False,
            center       = False,
            focus        = False,
            margin       = True,
            bind_esc     = False,
            **kwargs
        )

        self.method        = method
        self.show_cancel   = show_cancel
        self.message_key   = message_key
        self.window        = None
        self.thread        = None
        self.result_state  = result_state
        self.send_emits    = send_emits
        self.current_state = AppState.AS_NONE   \
            if result_state == AppState.AS_NONE \
            else GlobalData.current_state()

        GlobalData.set_current_state(AppState.AS_BUSY)

        if self.method:
            self.__create_window()

    def __enter__(self):
        if self.send_emits and hasattr(AppThreadExecutor, 'emit_started') and callable(getattr(AppThreadExecutor, 'emit_started')):
            AppThreadExecutor.emit_started()

        self.root.after(10, self.__execute_method)

        if self.window:
            self.window.show()
        elif self.message_key:
            VolatileMessage(text=gtbk(self.message_key))

    def __exit__(self, *_):
        AppThreadExecutor.__reset_cursor()
        if self.send_emits and hasattr(AppThreadExecutor, 'emit_finished') and callable(getattr(AppThreadExecutor, 'emit_finished')):
            AppThreadExecutor.emit_finished()
        if self.result_state or self.current_state != AppState.AS_NONE:
            GlobalData.set_current_state(self.result_state if self.result_state else self.current_state)

    def __execute_method(self):
        AppThreadExecutor.__set_busy_cursor(window=self.window.root if self.window else None)
        AppThreadExecutor.running = True
        self.thread = Thread(target=self.method)
        self.thread.daemon = True
        self.thread.start()
        self.__tread_checker()

    def __tread_checker(self):
        if not self.thread.is_alive():
            self.__close()
        else:
            self.root.after(200, self.__tread_checker)

    @staticmethod
    def __set_busy_cursor(window):
        if window:
            window.configure(cursor='watch')
        GlobalData.main_window.configure(cursor='watch')
        GlobalData.main_window.update()

    @staticmethod
    def __reset_cursor():
        if GlobalData.main_window.children:
            GlobalData.main_window.configure(cursor='')
            GlobalData.main_window.update()

    def __create_window(self):
        self.window = CwcTopLevel(create_frame=True, center=False, bind_esc=False)
        self.window.frame().Label(text=gtbk(self.message_key), size=10, row=0, col=0)
        if self.show_cancel:
            CwcButtonTkmt(
                master           = self.window.frame(),
                image_base_name  = 'close',
                command          = self.__close,
                row              = 1,
                col              = 0,
                sticky           = tk.N,
                pady             = (0,5),
                busy_is_disabled = False
            )

    def __close(self):
        AppThreadExecutor.running = False
        if self.window:
            self.__exit__()
            self.window.quit()


########################

def test_method():
    for i in range(30):
        if not AppThreadExecutor.running:
            break
        print(i)
        sleep(1)

def test():
    with AppThreadExecutor(show_cancel=True, method=test_method, message_key='filling_words'):
        pass

if __name__ == "__main__":
    from cwc_style import set_style

    root = GlobalData.main_tkmt_window

    bind(GlobalData, lambda *_: print('emit_state_changed'), 'emit_state_changed')

    set_style()

    root.Button(text='test', command=test)

    root.run()
