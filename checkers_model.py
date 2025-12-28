class CheckersModel:
    def __init__(self):
        self.board = []
        self.turn = 1  # 1 - Белые, 2 - Черные
        self.white_left = 12
        self.black_left = 12
        self.winner = None
        self.consecutive_capture = False
        self.last_moved_piece = None
        self.create_board()

    def create_board(self):
        # 0-пусто, 1-белая, 2-черная, 3-белая дамка, 4-черная дамка
        self.board = [[0] * 8 for _ in range(8)]
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    if row < 3: self.board[row][col] = 2
                    elif row > 4: self.board[row][col] = 1

    def change_turn(self):
        if self.consecutive_capture:
            return # Если нужно бить дальше, ход не меняем
        self.turn = 2 if self.turn == 1 else 1
        self.check_win()

    def check_win(self):
        if self.white_left <= 0: self.winner = "Черные победили!"
        elif self.black_left <= 0: self.winner = "Белые победили!"
        # Тут можно добавить проверку на отсутствие ходов (пат)

    def get_valid_moves(self, row, col):
        """Возвращает словарь доступных ходов для шашки (r, c): { (target_r, target_c): [captured_pieces] }"""
        piece = self.board[row][col]
        if piece == 0 or (piece % 2 != self.turn % 2):
            return {}

        moves = {}
        # Если идет серийная рубка, разрешено ходить только последней шашкой
        if self.consecutive_capture and (row, col) != self.last_moved_piece:
            return {}

        is_king = piece > 2
        # Направления для шашек и дамок
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Все 4 диагонали
        
        # Для обычных шашек ограничиваем направления движения (но не рубки)
        if not is_king:
            move_dirs = [(-1, -1), (-1, 1)] if self.turn == 1 else [(1, -1), (1, 1)]
        else:
            move_dirs = directions

        # 1. Поиск ходов без рубки (только если нет серийной рубки)
        if not self.consecutive_capture:
            for dr, dc in (directions if is_king else move_dirs):
                r, c = row + dr, col + dc
                if self._is_valid_pos(r, c) and self.board[r][c] == 0:
                    moves[(r, c)] = []
                    # Для дамок продолжаем искать по диагонали
                    if is_king:
                        r, c = r + dr, c + dc
                        while self._is_valid_pos(r, c) and self.board[r][c] == 0:
                            moves[(r, c)] = []
                            r, c = r + dr, c + dc

        # 2. Поиск ходов с рубкой (приоритет)
        captures = self._get_captures(row, col, is_king)
        if captures:
            # Если есть рубка, обычные ходы запрещены (правило обязательной рубки)
            return captures
        
        # Если есть глобальная обязательная рубка на доске другой шашкой, 
        # то этой ходить нельзя (если она сама не рубит)
        if self._check_global_mandatory_capture(row, col):
            return {}

        return moves

    def _get_captures(self, row, col, is_king):
        """Поиск возможных рубок для конкретной фигуры"""
        captures = {}
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            
            # Логика для Дамки (летит до первой фигуры)
            if is_king:
                while self._is_valid_pos(r, c) and self.board[r][c] == 0:
                    r += dr
                    c += dc
            
            if self._is_valid_pos(r, c):
                enemy = self.board[r][c]
                # Если встретили врага
                if enemy != 0 and (enemy % 2 != self.turn % 2):
                    landing_r, landing_c = r + dr, c + dc
                    # Проверяем место за врагом
                    steps = []
                    while self._is_valid_pos(landing_r, landing_c) and self.board[landing_r][landing_c] == 0:
                        steps.append((landing_r, landing_c))
                        if not is_king: break # Обычная шашка падает сразу за врагом
                        landing_r += dr
                        landing_c += dc
                    
                    for lr, lc in steps:
                        captures[(lr, lc)] = [(r, c)] # Записываем, кого съели
        return captures

    def _check_global_mandatory_capture(self, current_r, current_c):
        """Проверяет, есть ли на доске другие шашки, которые ОБЯЗАНЫ бить"""
        if self.consecutive_capture: return False 
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != 0 and (piece % 2 == self.turn % 2):
                    if (r, c) == (current_r, current_c): continue # Себя не проверяем
                    is_king = piece > 2
                    if self._get_captures(r, c, is_king):
                        return True # Кто-то другой обязан бить
        return False

    def _is_valid_pos(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def make_move(self, start_pos, end_pos, captured):
        r1, c1 = start_pos
        r2, c2 = end_pos
        piece = self.board[r1][c1]
        
        # Перемещение
        self.board[r1][c1] = 0
        self.board[r2][c2] = piece
        
        # Удаление съеденных
        captured_occurred = False
        if captured:
            captured_occurred = True
            for cr, cc in captured:
                if self.board[cr][cc] != 0:
                    if self.board[cr][cc] <= 2: # Обычные
                        if self.board[cr][cc] == 1: self.white_left -= 1
                        else: self.black_left -= 1
                    else: # Дамки
                        if self.board[cr][cc] == 3: self.white_left -= 1
                        else: self.black_left -= 1
                    self.board[cr][cc] = 0

        # Превращение в дамку
        promoted = False
        if piece == 1 and r2 == 0:
            self.board[r2][c2] = 3
            promoted = True
        elif piece == 2 and r2 == 7:
            self.board[r2][c2] = 4
            promoted = True
            
        # Логика серийной рубки
        is_king = self.board[r2][c2] > 2
        can_capture_more = False
        if captured_occurred:
            new_captures = self._get_captures(r2, c2, is_king)
            if new_captures:
                can_capture_more = True
        
        if captured_occurred and can_capture_more:
            self.consecutive_capture = True
            self.last_moved_piece = (r2, c2)
            # В русских шашках если стал дамкой во время боя - бьешь дальше как дамка
        else:
            self.consecutive_capture = False
            self.last_moved_piece = None
            self.change_turn()
            
        return captured_occurred