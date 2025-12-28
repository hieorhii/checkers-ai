import tkinter as tk

class CheckersView:
    def __init__(self, root, model):
        self.model = model
        self.root = root
        self.cell_size = 70
        self.canvas = tk.Canvas(root, width=8*self.cell_size, height=8*self.cell_size)
        self.canvas.pack()
        self.status_label = tk.Label(root, text="Ход белых", font=("Arial", 14))
        self.status_label.pack()
        
        self.selected_piece = None # (row, col)
        self.valid_moves = {}      # Словарь доступных ходов для выделенной шашки

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#F0D9B5", "#B58863"] # Цвета как в шахматах
        
        for r in range(8):
            for c in range(8):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                color = colors[(r + c) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Рисуем подсветку возможных ходов (зеленые точки)
                if (r, c) in self.valid_moves:
                    self.canvas.create_oval(x1+25, y1+25, x2-25, y2-25, fill="green", outline="")

                # Рисуем шашки
                piece = self.model.board[r][c]
                if piece != 0:
                    self.draw_piece(x1, y1, x2, y2, piece, (r, c) == self.selected_piece)

        # Обновляем текст
        if self.model.winner:
            self.status_label.config(text=self.model.winner, fg="red")
        else:
            turn_text = "Ход белых" if self.model.turn == 1 else "Ход черных"
            self.status_label.config(text=turn_text, fg="black")

    def draw_piece(self, x1, y1, x2, y2, piece, is_selected):
        pad = 8
        fill_color = "white" if piece in [1, 3] else "black"
        outline_color = "green" if is_selected else "gray"
        width = 4 if is_selected else 1
        
        self.canvas.create_oval(x1+pad, y1+pad, x2-pad, y2-pad, 
                                fill=fill_color, outline=outline_color, width=width)
        
        # Обозначение дамки (золотой кружок внутри)
        if piece in [3, 4]:
            self.canvas.create_oval(x1+pad+15, y1+pad+15, x2-pad-15, y2-pad-15, 
                                    fill="gold", outline="black")

    def on_click(self, event):
        if self.model.winner: return

        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        # 1. Клик по зеленой точке (ход)
        if (row, col) in self.valid_moves:
            captured = self.valid_moves[(row, col)]
            self.model.make_move(self.selected_piece, (row, col), captured)
            self.selected_piece = None
            self.valid_moves = {}
            
            # Если после хода шашка должна бить дальше, выбираем её автоматически
            if self.model.consecutive_capture:
                 self.selected_piece = self.model.last_moved_piece
                 self.valid_moves = self.model.get_valid_moves(*self.selected_piece)
            
            self.draw_board()
            return

        # 2. Клик по своей шашке (выбор)
        piece = self.model.board[row][col]
        if piece != 0 and (piece % 2 == self.model.turn % 2):
            self.selected_piece = (row, col)
            self.valid_moves = self.model.get_valid_moves(row, col)
            self.draw_board()