import os
import sys

class GameConfigs:
    _instance = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = GameConfigs()
        return cls._instance

    @staticmethod
    def width():
        return GameConfigs._get_instance()._width

    @staticmethod
    def height():
        return GameConfigs._get_instance()._height

    @staticmethod
    def get_config_value(name:str):
        if name:
            if name[0] != "_":
                name = f"_{name}"
            if hasattr(GameConfigs._get_instance(), name):
                return GameConfigs._get_instance().__getattribute__(name)
            else:
                print(f"WARNING: In GameConfigs attribute \"{name}\" is not exists!")
                return None


    def __init__(self):
        self._configs_path = os.path.abspath( os.path.join(os.path.abspath(__file__), "../../configs.txt") )
        if not os.path.exists(self._configs_path) or os.stat(self._configs_path).st_size == 0:
            with open(self._configs_path, "w", encoding="utf-8") as cfg:
                cfg.write(self._default_configs())
        self._parse()

    def _parse(self):
        def parse_value(v:str):
            if v.lower() == "true":
                return True
            if v.lower() == "false":
                return False
            is_int = True
            is_float = True
            dot_found = False
            has_digit = False
            for i in range(len(v)):
                s = v[i]
                if s.isdigit():
                    has_digit = True
                    continue
                if i == 0 and (s == "-" or s == "."):
                    if s == ".":
                        is_int = False
                        dot_found = True
                    continue
                if i == 0:
                    is_int = False
                    is_float = False
                    break
                else:
                    if not dot_found and s == ".":
                        is_int = False
                        dot_found = True
                        continue
                    is_int = False
                    is_float = False
                    break
            if is_int and has_digit:
                return int(v)
            if is_float and has_digit:
                return float(v)
            return v

        with open(self._configs_path, "r", encoding="utf-8") as cfg:
            while True:
                line = cfg.readline()
                if line == "":
                    break
                line = line.lstrip()
                if line == "" or line[0] == "#" or line.find("=") == -1:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = parse_value(value.strip())
                self.__setattr__(f"_{key}", value)


    def _save(self):
        ...

    def _default_configs(self)->str:
        return """# Generated default config file. Key=Value, lines start with # will be ignored.
width=600
height=600
rotate_text_on_selector=true
remove_used_nums_from_selector=true
"""
