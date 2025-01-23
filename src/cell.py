import tkinter
import tkinter.font
from .game_configs import GameConfigs

class Cell:
    _size = None
    _offset = None

    @staticmethod
    def size()->None | float:
        return Cell._size

    @staticmethod
    def offset()->None | float:
        return Cell._offset

    def __init__(self, canvas:tkinter.Canvas, x:int, y:int, size:float, offset:float, init_value:int = 0):
        if Cell._offset is None:
            Cell._offset = offset
        if Cell._size is None:
            Cell._size = size
        self.canvas = canvas
        self.id = y * 9 + x + 1
        offset_x = x // 3
        offset_y = y // 3
        rx = x * size + offset + offset_x
        ry = y * size + offset + offset_y
        if (offset_x + offset_y) % 2 == 0:
            self.fill_color = "#d0d0d0"
        else:
            self.fill_color = "#c0c0c0"
        self.highlight_color = "#9ed3ff"
        self.highlight_num_color = "#8bbae0"
        self.current_fill_color = self.fill_color
        self.rect_id = canvas.create_rectangle(rx, ry, rx + size, ry + size, outline="#707070", fill=self.current_fill_color)
        self.text_id = None
        self.text_shadow = None
        self._left = rx
        self._top = ry
        self._font = tkinter.font.Font(canvas, size=24, weight=tkinter.font.NORMAL)
        if init_value != 0:
            self._editable = False
            self._current_value = init_value
            self.changeValue()
        else:
            self._editable = True
            self._current_value = 0
        self.allowed_numbers = [i for i in range(1, 10)]
        self._selector = None


    @property
    def index(self)->int:
        return self.id - 1

    @property
    def editable(self)->bool:
        return self._editable

    @property
    def str_current_value(self)->str:
        return "" if self._current_value == 0 else str(self._current_value)

    @property
    def current_value(self)->int:
        return self._current_value

    @current_value.setter
    def current_value(self, v:int):
        if not self._editable:
            return
        self._current_value = v
        self.changeValue()

    @property
    def column(self)->int:
        return (self.id - 1) % 9

    @property
    def row(self)->int:
        return (self.id - 1) // 9


    def set_permanent(self, value:int):
        is_num = [i for i in range(1, 10)].count(value) > 0
        if is_num and self.editable:
            self._current_value = value
            self._editable = False
            self.changeValue()
            if self.text_shadow is None:
                self.canvas.itemconfigure(self.text_id, fill="green")
                self._create_text_shadow()
        elif is_num:
            self._current_value = value
            self._update_texts()

    def set_impermanent(self, value:int=0):
        self._current_value = value
        if not self.editable:
            self._editable = True
            self.canvas.delete(self.text_shadow)
            self.text_shadow = None
            self.canvas.itemconfigure(self.text_id, fill="black")
        self._update_texts()

    def set_visibility(self, is_visible:bool):
        visible = tkinter.HIDDEN if not is_visible else tkinter.NORMAL
        if self.text_id:
            self.canvas.itemconfigure(self.text_id, state=visible)
        if self.text_shadow:
            self.canvas.itemconfigure(self.text_shadow, state=visible)
        if self._selector:
            self._selector.set_visibility(visible)

    def _update_texts(self):
        if self.text_id:
            self.canvas.itemconfig(self.text_id, text=self.str_current_value)
        if self.text_shadow:
            self.canvas.itemconfig(self.text_shadow, text=self.str_current_value)

    def _create_text_shadow(self):
        if not self.editable:
            self.text_shadow = self.canvas.create_text(self._left + Cell.size() / 2 + 1,
                                                       self._top + Cell.size() / 2 + 1,
                                                       text=self.str_current_value,
                                                       anchor=tkinter.CENTER,
                                                       justify=tkinter.CENTER,
                                                       fill="#707070",
                                                       font=self._font)
            self.canvas.tag_lower(self.text_shadow, self.text_id)

    def changeValue(self):
        if self.text_id:
            self._update_texts()
        else:
            self.text_id = self.canvas.create_text(self._left + Cell.size() / 2,
                                                   self._top + Cell.size() / 2,
                                                   text=self.str_current_value,
                                                   anchor=tkinter.CENTER,
                                                   justify=tkinter.CENTER,
                                                   fill="black" if self.editable else "green",
                                                   font=self._font)
            self.canvas.tag_raise(self.text_id, self.rect_id)
            self._create_text_shadow()

    def is_overlap(self, x:float, y:float)->bool:
        return self._left < x < self._left + Cell.size() and self._top < y < self._top + Cell.size()

    def activate(self, x:float, y:float):
        self.canvas.itemconfigure(self.rect_id, fill="#ff0000")
        self._selector = Selector(self, self.canvas, x, y, self.allowed_numbers)

    def deactivate(self):
        self.canvas.itemconfigure(self.rect_id, fill=self.current_fill_color)
        if self._selector:
            self._selector.destroy()
            self._selector = None

    def selector_mouse_pos(self, x:float, y:float, button_pressed:bool):
        if self._selector:
            self._selector.mouse_pos(x, y, button_pressed)

    def check_selector_choice(self)->bool:
        if self._selector:
            return self._selector.check_choice()
        return False

    def accept_selector_choice(self):
        if self.editable and self._selector:
            v = self._selector.get_choosed_value()
            self._current_value = 0 if v == "x" else int(v)
            self.changeValue()

    def set_highligh(self, enable:bool, is_num:bool=False):
        if not GameConfigs.get_config_value("highlight_mouse_pos_sectors"):
            return
        self.current_fill_color = (self.highlight_num_color if is_num  else self.highlight_color) if enable else self.fill_color
        self.canvas.itemconfigure(self.rect_id, fill=self.current_fill_color)


from .selector import Selector
