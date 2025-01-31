import tkinter

from src.main_frame import GameMainFrame
from src.game_configs import GameConfigs
from src.texts import Texts


class CheatsWindow(tkinter.Toplevel):
    def __init__(self, parent, main_frame:GameMainFrame, restore_visibility:bool):
        super().__init__(parent)
        self.title(Texts.get("configure"))
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_delete_window)

        self.parent = parent
        self.main_frame = main_frame
        self._restore_visibility = restore_visibility
        self.focus()

        self.resizable(False, False)

    def on_delete_window(self):
        if self._restore_visibility:
            self.main_frame.toggle_visibility()
        self.destroy()

