from .cell import Cell

class Groups:
    def __init__(self):
        self.horizontals = []
        self.verticals = []
        self.squares = []

        for r in range(9):
            self.horizontals.append([])
            for c in range(9):
                i = r * 9 + c
                # horizontals
                self.horizontals[r].append(i)
                # verticals
                if r == 0:
                    self.verticals.append([c])
                else:
                    self.verticals[c].append(i)
                # squares
                if c % 3 == 0 and r % 3 == 0:
                    self.squares.append([i])
                else:
                    self.squares[3 * (r // 3) + c // 3].append(i)

    def get_indexes(self, c:Cell)->set[int]:
        indexes:set = set()
        indexes.update(self.horizontals[c.row])
        indexes.update(self.verticals[c.column])
        indexes.update(self.squares[3 * (c.row // 3) + c.column // 3])
        return indexes


class Checker:
    def __init__(self, all_cells:list[Cell]):
        self.cells = all_cells
        self._groups = Groups()

    def get_allowed_nums(self, c:Cell)->list[int]:
        allows = [i for i in range(1, 10)]
        dep_indexes = self._groups.get_indexes(c)
        for di in dep_indexes:
            cv = self.cells[di].current_value
            if cv == 0:
                continue
            if allows.count(cv) > 0:
                allows.remove(cv)
        return allows

    def correct_cell_value(self, c:Cell)->bool:
        indexes = self._groups.get_indexes(c)
        for index in indexes:
            other = self.cells[index]
            if c != other:
                if other.current_value == 0 or c.current_value == 0 or other.current_value == c.current_value:
                    return False
        return True

    def get_cell_groups_indexes(self, c:Cell)->set[int]:
        return self._groups.get_indexes(c)