import tkinter
from src.game_configs import GameConfigs
from src.main_frame import GameMainFrame

if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Sudoku")
    root.geometry("1024x768")
    game = GameMainFrame(root, GameConfigs.width(), GameConfigs.height())
    game.drawBoard()
    root.mainloop()
