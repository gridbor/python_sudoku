import tkinter
from tkinter import ttk
import tkinter.font
import time

class ControlFrame(ttk.Frame):
    def __init__(self, parent, refresh_callback = None, visibility_callback = None):
        super().__init__(parent)

        self.parent = parent
        self.pause_textvar = tkinter.StringVar(self, "Pause")
        self.timer_textvar = tkinter.StringVar(self, "0")

        self.refresh_button = ttk.Button(self, text="Refresh", command=refresh_callback)
        self.refresh_button.pack(side=tkinter.LEFT)
        self.pause_button = ttk.Button(self, textvariable=self.pause_textvar, command=visibility_callback)
        self.pause_button.pack(side=tkinter.LEFT, after=self.refresh_button)
        self.timer_label = ttk.Label(self, textvariable=self.timer_textvar, font=tkinter.font.Font(self, size=12))
        self.timer_label.pack(after=self.pause_button, anchor=tkinter.E, side=tkinter.RIGHT)

        self._is_timer_run = False
        self._create_time = time.time_ns()
        self._start_time = None
        self._current_time = 0
        self.show_ms = True

    def start_timer(self):
        if self._is_timer_run:
            return
        self._start_time = time.time_ns()
        self._is_timer_run = True
        self.timer_update()

    def stop_timer(self):
        if not self._is_timer_run:
            return
        self._is_timer_run = False

    def reset_timer(self):
        self._current_time = 0

    def timer_update(self):
        if not self._is_timer_run:
            return
        delta_time = time.time_ns() - self._start_time
        self._current_time += delta_time
        self._start_time = time.time_ns()
        self.after(33 if self.show_ms else 200, self.timer_update)

        seconds = self._current_time // (10 ** 9)
        sec = seconds % 60
        min = (seconds // 60) % 60
        hours = seconds // 3600
        timer_str = ""
        if hours > 0:
            timer_str += f"{hours}:"
        if min > 0 or timer_str:
            if timer_str:
                timer_str += f"{min:02d}:"
            else:
                timer_str += f"{min}:"
        if timer_str:
            timer_str += f"{sec:02d}"
        else:
            timer_str += str(sec)
        if self.show_ms:
            ms = (self._current_time % (10 ** 9)) // (10 ** 6)
            timer_str += f".{ms:03d}"
        self.timer_textvar.set(timer_str)
