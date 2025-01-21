import tkinter
from tkinter import ttk
import random
import time
import os
from .game_configs import GameConfigs
from .gui.ControlFrame import ControlFrame

class InitialData:
    def __init__(self):
        self._data_path = os.path.abspath( os.path.join(os.path.abspath(__file__), "../../initial_data.txt") )
        if not os.path.exists(self._data_path):
            with open(self._data_path, "w") as data:
                data.write("")
        with open(self._data_path, "r") as data:
            all_lines = data.readlines()
            al = len(all_lines)
            if al > 0:
                i = random.randrange(0, al)
                self._current_data = all_lines[i].strip()
            else:
                self._current_data = ""

    def get_value(self, x:int, y:int)->int:
        if self._current_data:
            for i in range(0, len(self._current_data), 3):
                if x == int(self._current_data[i]) and y == int(self._current_data[i + 1]):
                    return int(self._current_data[i + 2])
        return 0


class GameMainFrame:
    FRAME_WIDTH:float
    FRAME_HEIGHT:float

    def __init__(self, parent:tkinter.Tk, w:float, h:float):
        GameMainFrame.FRAME_WIDTH = w
        GameMainFrame.FRAME_HEIGHT = h
        self.parent = parent
        self.frame_offset = 90
        fw = w + self.frame_offset + 1
        fh = h + self.frame_offset + 1

        self.control_frame = ControlFrame(parent, self.refresh, self.toggle_visibility)
        self.control_frame.grid(column=0, row=0, columnspan=2, sticky=tkinter.N + tkinter.EW)

        parent.wait_visibility(self.control_frame)
        parent.minsize(fw, fh + self.control_frame.winfo_height())

        self.canvas = tkinter.Canvas(parent, highlightthickness=0, borderwidth=0, width=fw, height=fh)
        self.canvas.grid(row=1, column=1, sticky=tkinter.NSEW)
        self.canvas.bind("<ButtonPress-1>", lambda event: self.mouseEvent("pressed", event))
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.mouseEvent("released", event))
        self.canvas.bind("<Motion>", lambda event: self.mouseEvent("move", event))
        self.canvas.create_rectangle(0, 0, fw, fh, fill="#fcfcfc")

        parent.columnconfigure([0,1], weight=1)
        parent.rowconfigure([0,1], weight=1)

        self.cells:list[Cell] = []
        self.checker = None
        self.selected_cell:Cell = None
        self._press_time = None
        self._initial_data = None
        self._board_visible = True

    def drawBoard(self):
        ms = min(GameMainFrame.FRAME_WIDTH, GameMainFrame.FRAME_HEIGHT)
        s = ms // 9
        o = (ms - s * 9) / 2 - 1 + self.frame_offset / 2
        if self._initial_data is None:
            self._initial_data = InitialData()
        for i in range(9):
            for j in range(9):
                c = Cell(self.canvas, j, i, s, o, self._initial_data.get_value(j, i))
                self.cells.append(c)
        self.checker = Checker(self.cells)
        self.control_frame.start_timer()

    def refresh(self):
        self.clear_board()
        self.parent.focus()
        self.control_frame.reset_timer()

    def clear_board(self):
        for c in self.cells:
            c.current_value = 0

    def set_board_visibility(self, visible:bool):
        if self._board_visible == visible:
            return
        self._board_visible = visible
        for c in self.cells:
            c.set_visibility(visible)
        if visible:
            self.control_frame.start_timer()
        else:
            self.control_frame.stop_timer()

    def toggle_visibility(self):
        self.set_board_visibility(not self._board_visible)
        self.parent.focus()

    def mouseEvent(self, type, event):
        # MOUSE MOTION
        if type == "move":
            if self.selected_cell:
                self.selected_cell.selector_mouse_pos(event.x, event.y, event.state & 0x100 != 0)

        # PRESS MOUSE BUTTON
        elif type == "pressed":
            old_select = None
            if self.selected_cell:
                old_select = self.selected_cell
                self.selected_cell = None
            for c in self.cells:
                if c.is_overlap(event.x, event.y):
                    if not c.editable:
                        break
                    self.selected_cell = c
                    self._press_time = time.time()
                    break
            is_selector_pressed = False
            if old_select:
                is_selector_pressed = old_select.check_selector_choice(event.x, event.y, True)
                if is_selector_pressed:
                    old_select.accept_selector_choice()
                    self.check_completed()
                if self.selected_cell and self.selected_cell.id == old_select.id:
                    self.selected_cell.deactivate()
                    self.selected_cell = None
                    self._press_time = None
                else:
                    old_select.deactivate()
            if is_selector_pressed:
                self.selected_cell = None
                self._press_time = None
            if self.selected_cell:
                if GameConfigs.get_config_value("remove_used_nums_from_selector"):
                    self.selected_cell.allowed_numbers = self.checker.get_allowed_nums(self.selected_cell)
                self.selected_cell.activate(event.x, event.y)

        # RELEASE MOUSE BUTTON
        elif type == "released":
            if self.selected_cell:
                if self._press_time:
                    if time.time() - self._press_time < 0.4:
                        self._press_time = None
                        return
                if self.selected_cell.check_selector_choice(event.x, event.y, False):
                    self.selected_cell.accept_selector_choice()
                    self.check_completed()
                self.selected_cell.deactivate()
                self._press_time = None
            self.selected_cell = None


    def check_completed(self):
        ...


from .checker import Checker
from .cell import Cell
