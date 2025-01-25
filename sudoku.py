import tkinter
from src.game_configs import GameConfigs
from src.main_frame import GameMainFrame
from src.texts import Texts


def update_texts():
    root.title(Texts.get("sudoku", "Sudoku"))
    game.update_texts()
    game.control_frame.update_texts()


if __name__ == "__main__":
    Texts.instance().load_locale(GameConfigs.get_config_value("language"))
    Texts.instance().set_update_texts(update_texts)

    root = tkinter.Tk()
    root.title(Texts.get("sudoku", "Sudoku"))
    root.geometry("1024x768")
    game = GameMainFrame(root, GameConfigs.width(), GameConfigs.height())
    game.drawBoard()
    root.mainloop()
