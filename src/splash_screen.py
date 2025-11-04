"""Module to handle the application starting splashscreen"""

import os
import tkinter as tk
from PIL import Image, ImageTk

from cwc_globals import (
    GlobalData,
    center_window
)

class SplashScreen:
    """Class to handle the application starting splashscreen"""

    def __init__(self) -> None:
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', 'true')

        image = Image.open(os.path.join(GlobalData.ROOT_DIR, 'images/cwc.jpg'))
        self.image = ImageTk.PhotoImage(image)

        tk.Label(master=self.window, image=self.image).pack()

        center_window(win=self.window, to_screen=True)

        parent_name   = self.window.winfo_parent()
        parent_widget = self.window.nametowidget(parent_name)
        # hide the horrible tk window behind the splash_screen
        center_window(win=parent_widget, to_screen=True)

        self.window.configure(cursor='wait')

        self.window.update()

    def close(self):
        self.window.destroy()
        self.window.update()


############# TESTS #############

if __name__ == "__main__":
    import time
    sc = SplashScreen()
    time.sleep(5)
