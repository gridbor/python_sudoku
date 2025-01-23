import tkinter
from tkinter import ttk
import tkinter.font
import random
import time
import os
from .game_configs import GameConfigs


class InitialData:
    def __init__(self):
        self._data_path = os.path.abspath( os.path.join(os.path.abspath(__file__), "../../initial_data.txt") )
        if not os.path.exists(self._data_path):
            with open(self._data_path, "w") as data:
                data.write("")
        with open(self._data_path, "r") as data:
            self._all_lines = data.readlines()
            al = len(self._all_lines)
            if al > 0:
                i = random.randrange(0, al)
                self._current_index = i
                self._current_data = self._all_lines[i].strip()
            else:
                self._current_data = ""

    def new_random_data(self):
        al = [i for i in range(len(self._all_lines))]
        al.remove(self._current_index)
        self._current_index = random.choice(al)
        self._current_data = self._all_lines[self._current_index].strip()

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

        parent.columnconfigure([0], weight=1)
        parent.rowconfigure([0,1], weight=1)

        self.control_frame = ControlFrame(parent, self)
        self.control_frame.grid(row=0, column=0, sticky=tkinter.N + tkinter.EW)

        parent.wait_visibility(self.control_frame)
        parent.maxsize(fw, fh + self.control_frame.winfo_height())
        parent.minsize(fw, fh + self.control_frame.winfo_height())

        self.canvas = tkinter.Canvas(parent, highlightthickness=0, borderwidth=0, width=fw, height=fh)
        self.canvas.grid(row=1, column=0, sticky=tkinter.NSEW)
        self.canvas.bind("<ButtonPress-1>", lambda event: self.mouseEvent("pressed", event))
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.mouseEvent("released", event))
        self.canvas.bind("<Motion>", lambda event: self.mouseEvent("move", event))
        self.canvas.create_rectangle(0, 0, fw, fh, fill="#fcfcfc")
        self._win_text = self.canvas.create_text(fw / 2, self.frame_offset / 4, anchor=tkinter.CENTER, justify=tkinter.CENTER, state=tkinter.HIDDEN, fill="red", text="SOLVED!", font=tkinter.font.Font(self.canvas, size=16))

        self.cells:list[Cell] = []
        self.checker = None
        self.selected_cell:Cell = None

        self._press_time = None
        self._initial_data = None
        self._board_visible = True
        self._game_over = False
        self._on_mouse_over_cell:Cell = None


    @property
    def board_visible(self)->bool:
        return self._board_visible

    @property
    def is_game_over(self)->bool:
        return self._game_over


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
        self.control_frame.show_ms = True
        self.control_frame.start_timer()
        if self._game_over:
            self._game_over = False
            self.canvas.itemconfigure(self._win_text, state=tkinter.HIDDEN)

    def new_game(self):
        self._initial_data.new_random_data()
        self.control_frame.reset_timer()
        self.clear_board(True)
        if not self._board_visible:
            self.set_board_visibility(True)
        self.parent.focus()

    def refresh(self):
        self.control_frame.reset_timer()
        self.clear_board()
        self.parent.focus()
        if not self._board_visible:
            self.set_board_visibility(True)

    def clear_board(self, force:bool=False):
        for c in self.cells:
            if force:
                c.set_impermanent()
                c.set_permanent(self._initial_data.get_value(c.column, c.row))
            else:
                c.current_value = 0
        if self._game_over:
            self._game_over = False
            self.canvas.itemconfigure(self._win_text, state=tkinter.HIDDEN)
            self.control_frame.start_timer()

    def set_board_visibility(self, visible:bool):
        if self._board_visible == visible or self._game_over:
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

    def set_numbers_highlight(self, value:int, enabled:bool):
        if not GameConfigs.get_config_value("highlight_mouse_pos_sectors"):
            return
        for cell in self.cells:
            if cell.current_value != 0 and cell.current_value == value:
                cell.set_highligh(enabled, True)


    def mouseEvent(self, type, event):
        if self._game_over or not self.board_visible:
            return

        # MOUSE MOTION
        if type == "move":
            if self.selected_cell:
                self.selected_cell.selector_mouse_pos(event.x, event.y, event.state & 0x100 != 0)
            if GameConfigs.get_config_value("highlight_mouse_pos_sectors"):
                not_found = True
                highlight = None
                over_cell = None
                for c in self.cells:
                    if c.is_overlap(event.x, event.y):
                        if c == self._on_mouse_over_cell:
                            not_found = False
                            break
                        over_cell = c
                        highlight = "enable"
                        not_found = False
                        break
                if not_found and self._on_mouse_over_cell is not None:
                    highlight = "restore"
                if highlight is not None:
                    if self._on_mouse_over_cell is not None:
                        all_indexes = self.checker.get_cell_groups_indexes(self._on_mouse_over_cell)
                        for index in all_indexes:
                            self.cells[index].set_highligh(False)
                        self.set_numbers_highlight(self._on_mouse_over_cell.current_value, False)
                    if highlight == "enable":
                        all_indexes = self.checker.get_cell_groups_indexes(over_cell)
                        for index in all_indexes:
                            self.cells[index].set_highligh(True)
                        self.set_numbers_highlight(over_cell.current_value, True)
                    self._on_mouse_over_cell = over_cell

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
                is_selector_pressed = old_select.check_selector_choice()
                if is_selector_pressed:
                    self.set_numbers_highlight(old_select.current_value, False)
                    old_select.accept_selector_choice()
                    if Cell.offset() < event.x < Cell.offset() + Cell.size() * 9 + 2 and Cell.offset() < event.y < Cell.offset() + Cell.size() * 9 + 2:
                        if old_select.current_value != 0:
                            self.set_numbers_highlight(old_select.current_value, True)
                        else:
                            old_select.set_highligh(True)
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
                if self.selected_cell.check_selector_choice():
                    self.set_numbers_highlight(self.selected_cell.current_value, False)
                    self.selected_cell.accept_selector_choice()
                    if Cell.offset() < event.x < Cell.offset() + Cell.size() * 9 + 2 and Cell.offset() < event.y < Cell.offset() + Cell.size() * 9 + 2:
                        if self.selected_cell.current_value != 0:
                            self.set_numbers_highlight(self.selected_cell.current_value, True)
                        else:
                            self.selected_cell.set_highligh(True)
                    self.check_completed()
                self.selected_cell.deactivate()
                self._press_time = None
            self.selected_cell = None


    def check_completed(self):
        for c in self.cells:
            if c.current_value == 0:
                return
            if not self.checker.correct_cell_value(c):
                return
        self.control_frame.stop_timer()
        self.canvas.itemconfigure(self._win_text, state=tkinter.NORMAL)
        for c in self.cells:
            c.set_highligh(False)
        self._game_over = True


from .checker import Checker
from .cell import Cell
from .gui.ControlFrame import ControlFrame
