import os

class Texts():
    _instance=None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Texts()
        return cls._instance

    @staticmethod
    def get(key:str, default:str="")->str:
        value = Texts.instance().get_text(key)
        if value not in ["$NOT_FOUND$", "$NOT_EXIST$"]:
            return value
        if default == "":
            default = f"{key}_{value}"
        return default


    def __init__(self):
        self._locales_path = os.path.abspath( os.path.join(os.path.abspath(__file__), "../../assets/locales/") )

        self.current_locale = "en"
        self.locales = [x.lower()[:-4] for x in os.listdir(self._locales_path)]

        self._texts_update_callback = None
        self._default_texts = self._load()
        self._current_texts = {}

    def _load(self)->dict:
        result = {}
        found = False
        for locale in os.listdir(self._locales_path):
            if locale.lower() == f"{self.current_locale}.txt":
                found = True
                sep = "" if self._locales_path[-1] in ["/", "\\"] else "/"
                with open(f"{self._locales_path}{sep}{locale}", "r", encoding="utf-8") as locale_file:
                    while True:
                        line = locale_file.readline()
                        if line:
                            dd = line.find(":")
                            if dd != -1:
                                key = line[:dd]
                                value = line[dd + 1:-1]
                                result[key] = value
                                if key in self.locales:
                                    locale_index = self.locales.index(key)
                                    self.locales[locale_index] = { "key":key, "value":value }
                        else:
                            break
        if not found:
            print(f"WARNING: Locale \"{self.current_locale}\" not found!")
        return result

    def load_locale(self, lang:str):
        if self.current_locale == lang.lower():
            return

        self.current_locale = lang.lower()
        if lang.lower() == "en":
            self._current_texts = self._default_texts
        else:
            self._current_texts = self._load()

        if self._texts_update_callback is not None:
            self._texts_update_callback()

    def get_text(self, key:str):
        if not self._current_texts and not self._default_texts:
            print(f"ERROR: LOCALES NOT EXISTS IN \"{self._locales_path}\"!")
            return "$NOT_EXIST$"
        if key in self._current_texts:
            return self._current_texts[key]
        if key in self._default_texts:
            return self._default_texts[key]
        return "$NOT_FOUND$"

    def set_update_texts(self, callback):
        self._texts_update_callback = callback
