import tkinter
import tkinter.font
import math
from .game_configs import GameConfigs
from .cell import Cell

class Selector:
    destroy_animations = []

    def __init__(self, target:Cell, canvas:tkinter.Canvas, x:float, y:float, items:list[int|str]):
        self.cell = target
        self.canvas = canvas

        self._start_radius = 2
        self._finish_radius = Cell.size() / 6
        self._current_radius = self._start_radius
        self._step_radius = (self._finish_radius - self._start_radius) / 11
        self._direction = 1
        self._update_ms = 16

        self._cx = x
        self._cy = y
        self._items = items
        if items.count("x") <= 0:
            self._items.append("x")

        self._oval_id = None
        self._sectors = []
        self._num_font = None
        self._choosed_sector = None

        self.drawObjects()

        self._aidle_id = canvas.after(self._update_ms, self.update)


    def drawObjects(self):
        x = self._cx
        y = self._cy
        r = self._current_radius
        d = (r - self._start_radius) * 1.2

        if self._oval_id is None:
            self._oval_id = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#f0f0f0", outline="#909090", tags=("all", "selector"))
        else:
            self.canvas.coords(self._oval_id, [x - r, y - r, x + r, y + r])

        il = len(self._items)
        deg = (360 / il) if il > 1 else 180
        i = 0
        sr = Cell.size() / 2 + d
        if self._num_font is None:
            self._num_font = tkinter.font.Font(self.canvas, size=8)
        else:
            df = math.floor(d * 0.5)
            df = df if df % 2 == 0 else (df + 1)
            self._num_font.configure(size=8 + df)
        is_create = len(self._sectors) == 0
        for num in self._items:
            tx = sr * 0.7 * math.cos(math.radians(90 - deg * i))
            ty = sr * 0.7 * math.sin(math.radians(90 - deg * i))
            if is_create:
                sid = self.canvas.create_arc(x - sr, y - sr, x + sr, y + sr,
                                             fill="#f0f0f0" if num != "x" else "#cc2020", start=90 - deg * (i + 0.5), extent=deg,
                                             style=tkinter.PIESLICE, outline="#909090",
                                             tags=("all", "selector"))
                self.canvas.tag_lower(sid, self._oval_id)
                tid = self.canvas.create_text(x + tx, y - ty,
                                              angle=(-deg * i) if GameConfigs.get_config_value("rotate_text_on_selector") else 0,
                                              text=str(num),
                                              font=self._num_font,
                                              tags=("all", "selector"))
                self._sectors.append({ "arc_id":sid, "text_id":tid })
            else:
                self.canvas.coords(self._sectors[i]["arc_id"], [x - sr, y - sr, x + sr, y + sr])
                self.canvas.coords(self._sectors[i]["text_id"], [x + tx, y - ty])
            i += 1


    def destroy(self):
        Selector.destroy_animations.append(self)
        self._direction = -1
        if self._aidle_id is None:
            self._aidle_id = self.canvas.after(self._update_ms, self.update)


    def update(self):
        self._aidle_id = None
        self._current_radius += self._step_radius * self._direction
        is_finished = False
        if self._direction > 0 and self._current_radius >= self._finish_radius:
            self._current_radius = self._finish_radius
            is_finished = True
        elif self._direction < 0 and self._current_radius <= self._start_radius:
            self._current_radius = self._start_radius
            is_finished = True

        self.drawObjects()

        if not is_finished:
            self._aidle_id = self.canvas.after(self._update_ms, self.update)
        elif self._direction < 0:
            ids = [self._oval_id]
            ids.extend(self._sectors)
            for id in ids:
                if type(id) == int:
                    self.canvas.delete(id)
                else:
                    self.canvas.delete(id["arc_id"])
                    self.canvas.delete(id["text_id"])
            Selector.destroy_animations.remove(self)


    def _restore_choosed_sector(self):
        if self._choosed_sector:
            self.canvas.itemconfigure(self._choosed_sector["id"], fill=self._choosed_sector["restore_fill"])
            self._choosed_sector = None

    def mouse_pos(self, x:float, y:float, button_pressed:bool):
        lr = (self._cx - x)**2 + (self._cy - y)**2
        if lr <= self._finish_radius**2:
            self._restore_choosed_sector()
        else:
            if not button_pressed:
                br = Cell.size() / 2 + (self._finish_radius - self._start_radius) * 1.2
                if lr > br**2:
                    self._restore_choosed_sector()
                    return
            il = len(self._items)
            deg = (360 / il) if il > 1 else 180
            t = 0
            if self._cx == x:
                t = 90 if self._cy > y else 270
            else:
                t = 180 - math.degrees(math.atan2(self._cy - y, self._cx - x))
                if t < 0:
                    t += 360
            need_update = False
            sector_found = False
            for i in range(len(self._items)):
                start = float(self.canvas.itemcget(self._sectors[i]["arc_id"], "start"))
                if start < t < start + deg or start < t + 360 < start + deg:
                    if self._choosed_sector is None:
                        self._choosed_sector = {}
                        need_update = True
                    elif self._choosed_sector["id"] != self._sectors[i]["arc_id"]:
                        self.canvas.itemconfigure(self._choosed_sector["id"], fill=self._choosed_sector["restore_fill"])
                        need_update = True
                    sector_found = True
                    break
            if need_update and self._choosed_sector is not None:
                self._choosed_sector["id"] = self._sectors[i]["arc_id"]
                self._choosed_sector["restore_fill"] = self.canvas.itemcget(self._sectors[i]["arc_id"], "fill")
                self._choosed_sector["index"] = i
                self.canvas.itemconfigure(self._choosed_sector["id"], fill="#90f090")
            elif not sector_found:
                self._restore_choosed_sector()

    def check_choice(self)->bool:
        if self._choosed_sector:
            return True
        return False

    def get_choosed_value(self):
        if self._choosed_sector:
            s = self.canvas.itemcget(self._sectors[self._choosed_sector["index"]]["text_id"], "text")
            return s
        return None

    def set_visibility(self, visibility):
        self.canvas.itemconfigure("selector", state=visibility)
