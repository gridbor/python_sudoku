import tkinter
from tkinter import ttk
import tkinter.font
import time

from src.main_frame import GameMainFrame
from src.game_configs import GameConfigs
from src.texts import Texts


class ConfigureWindow(tkinter.Toplevel):
    def __init__(self, parent, main_frame:GameMainFrame, restore_visibility:bool):
        super().__init__(parent)
        self.title(Texts.get("configure"))
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_delete_window)

        self.parent = parent
        self.main_frame = main_frame
        self._restore_visibility = restore_visibility
        self._vars = []
        self.focus()

        rows = 0
        for param in GameConfigs.instance().params:
            label = ttk.Label(self, text=Texts.get(param["name"]), anchor=tkinter.NE)
            label.grid(row=rows, column=0, sticky=tkinter.NE, padx=2, pady=2)
            setattr(self, f"_{param['name']}&label", label)

            if type(param["value"]) is not bool:
                var = tkinter.StringVar(self, str(param["value"]), f"var_{param['name']}")
            else:
                var = tkinter.BooleanVar(self, param["value"], f"var_{param['name']}")
            self._vars.append({"param":param, "type":type(param["value"]), "variable":var})

            if type(param["value"]) is bool:
                value = ttk.Checkbutton(self, name=f"ui_{param['name']}", variable=var)
            elif param["name"] == "language":
                for locale in Texts.instance().locales:
                    if locale["key"] == var.get():
                        var.set(locale["value"])
                        break
                value = ttk.Combobox(self, name=f"ui_{param['name']}", textvariable=var, values=[x["value"] for x in Texts.instance().locales], state="readonly")
            else:
                value = ttk.Entry(self, name=f"ui_{param['name']}", textvariable=var, width=6 if type(param["value"]) in [int, float] else 20)
            value.grid(row=rows, column=1, padx=2, pady=2, sticky=tkinter.NW)
            setattr(self, f"_{param['name']}&value", value)
            rows += 1
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(row=rows, column=0, columnspan=2, padx=2, pady=2, sticky=tkinter.SE)
        self._apply_button = ttk.Button(self.buttons_frame, text=Texts.get("apply"), command=self.apply_configs)
        self._apply_button.pack(side=tkinter.RIGHT)
        self._cancel_button = ttk.Button(self.buttons_frame, text=Texts.get("cancel"), command=self.cancel_configs)
        self._cancel_button.pack(side=tkinter.RIGHT)
        self.resizable(False, False)

    def apply_configs(self):
        GameConfigs.instance().save(self._vars)
        self.on_delete_window()

    def cancel_configs(self):
        self.on_delete_window()

    def on_delete_window(self):
        if self._restore_visibility:
            self.main_frame.toggle_visibility()
        self.destroy()


class ControlFrame(ttk.Frame):
    def __init__(self, parent, main_frame:GameMainFrame):
        super().__init__(parent)

        self.parent_widget = parent
        self.main_frame = main_frame

        self.pause_textvar = tkinter.StringVar(self, Texts.get("pause"))
        self.timer_textvar = tkinter.StringVar(self, "0")

        self.new_game_button = ttk.Button(self, text=Texts.get("new_game"), command=main_frame.new_game)
        self.new_game_button.pack(side=tkinter.LEFT)
        self.refresh_button = ttk.Button(self, text=Texts.get("refresh"), command=main_frame.refresh)
        self.refresh_button.pack(side=tkinter.LEFT, after=self.new_game_button)
        self.cheats_button = ttk.Button(self, text=Texts.get("cheats"), command=self.show_cheats)
        self.cheats_button.pack(side=tkinter.LEFT, after=self.refresh_button)
        self.pause_button = ttk.Button(self, textvariable=self.pause_textvar, command=main_frame.toggle_visibility)
        self.pause_button.pack(side=tkinter.LEFT, after=self.cheats_button)
        self.config_button = ttk.Button(self, text=Texts.get("configure"), command=self.configure_callback)
        self.config_button.pack(side=tkinter.LEFT, after=self.pause_button)
        self.timer_label = ttk.Label(self, textvariable=self.timer_textvar, font=tkinter.font.Font(self, size=12))
        self.timer_label.pack(side=tkinter.RIGHT, after=self.pause_button)

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
        self.pause_button_update()

    def stop_timer(self):
        if not self._is_timer_run:
            return
        self._is_timer_run = False
        self.pause_button_update()

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

    def pause_button_update(self):
        if self.main_frame.is_game_over:
            return
        self.pause_textvar.set(Texts.get("pause") if self.main_frame.board_visible else Texts.get("resume"))

    def configure_callback(self):
        restore = False
        if self.main_frame.board_visible:
            self.main_frame.toggle_visibility()
            restore = True
        self.parent_widget.focus()
        ConfigureWindow(self.parent_widget, self.main_frame, restore)

    def show_cheats(self):
        ...


    def update_texts(self):
        self.pause_textvar.set(Texts.get("pause") if self.main_frame.board_visible else Texts.get("resume"))
        self.new_game_button.configure(text=Texts.get("new_game"))
        self.refresh_button.configure(text=Texts.get("refresh"))
        self.config_button.configure(text=Texts.get("configure"))
