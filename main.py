import tkinter as tk
from checkers_model import CheckersModel
from checkers_view import CheckersView

if __name__ == "__main__":
    root = tk.Tk()
    
    window_width = 8 * 70
    window_height = 8 * 70 + 40

    model = CheckersModel()
    view = CheckersView(root, model)

    root.mainloop()