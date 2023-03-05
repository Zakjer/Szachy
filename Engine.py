"""
Skrypt ten będzie odpowiedzialny za przechowywanie informacji o obecnym stanie gry. Będzie on również
determinował ruchy, które są legalne. Będzie także przechowywał dziennik aktywności.
"""

class StateOfTheGame:
    """Klasa ta odpowiada za wyświetlenie figur, szachownicy oraz za przechowywanie historii ruchów."""
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.white_to_move = True #Białe rozpoczynają partię
        self.move_log = []
    
    def make_move(self, move):
        """
        Funkcja bierze ruch jako parametr i wykonuje go (nie działa na roszadę, 
        promocję piona oraz bicie w przelocie)
        """
        self.board[move.start_row][move.start_column] = "--" #Pole, z którego ruszyła się figura staje się puste
        self.board[move.end_row][move.end_column] = move.piece_moved #Pole, na które ruszyła się figura
        self.move_log.append(move) #Zapisanie ruchu w historii
        self.white_to_move = not self.white_to_move #Gracze wykonują ruch na przemian

    def undo_move(self):
        """Funkcja cofająca ruch"""
        if len(self.move_log) != 0: #Sprawdzenie czy w parti został wykonany jakikolwiek ruch
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move #Zmiana wykonawcy ruchu 

    def get_valid_moves(self):
        """Wszystkie możliwe ruchy uwzględniające atak na króla(szach)"""
        return self.get_all_possible_moves()

    def get_all_possible_moves(self):
        """Wszystkie możliwe ruchy nie uwzględniające ataku na króla(szach)"""
        moves = []
        for row in range(len(self.board)): #Ilość rzędów
            for column in range(len(self.board[row])): #Ilość kolumn w danym rzędzie
                turn = self.board[row][column][0] #Ustalanie, który gracz powinien wykonać teraz ruch
                if (turn == "w" and self.white_to_move) and (turn == "b" and not self.white_to_move):
                    piece = self.board[row][column][1]
                    if piece == "p": #Ruchy dla piona
                        self.get_pawn_moves(row, column, moves)
                    elif piece == "R": #Ruchy dla wieży
                        self.get_rook_moves(row, column, moves)
                    elif piece == "N": #Ruchy dla skoczka
                        self.get_knight_moves(row, column, moves)
                    elif piece == "B": #Ruchy dla gońca
                        self.get_bishop_moves(row, column, moves)
                    elif piece == "Q": #Ruchy dla królowej
                        self.get_queen_moves(row, column, moves)
                    elif piece == "K": #Ruchy dla króla
                        self.get_king_moves(row, column, moves)
        return moves 

    def get_pawn_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla piona znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
        if self.white_to_move: #Ruchy białych pionów
            if self.board[row-1][column] == "--": #Ruch piona o jedno pole
                moves.append(Move((row, column), (row-1,column), self.board))
                if row == 6 and self.board[row-2][column] == "--": #Ruch piona o dwa pola
                    moves.append(Move((row, column), (row-2,column), self.board))



    def get_rook_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla wieży znajdującej się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
    pass 

    def get_knight_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla skoczka znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
    pass 

    def get_bishop_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla gońca znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
    pass 

    def get_queen_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla królowej znajdującej się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
    pass 

    def get_king_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla króla znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
    pass 


class Move:
    """Klasa ta odpowiada za wykonywanie ruchów"""
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()} #Zamiana współrzędnych listy na współrzędne
    files_to_columns = {"a":0, "b":1, "c":2, "d":3, #szachowe np. ([0,3] = a5)
                    "e":4, "f":5, "g":6, "h":7} 
    columns_to_files = {v: k for k, v in files_to_columns.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0] #Współrzędne pola, z którego figura się rusza
        self.start_column = start_sq[1]
        self.end_row = end_sq[0] #Współrzędne pola, na które figura się rusza
        self.end_column = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column] #Przechowywanie zdobytych figur
        self.move_id = (self.start_row * 1000 + self.start_column * 100 + 
        self.end_row * 10 + self.end_column) #Przypisanie ruchowi unikalnego id 

    def __eq__(self, other):
        """Funkcja porównująca ze sobą dwa obiekty"""
        if isinstance(other, Move):
            return self.move_id  == other.move_id 
        return False

    def get_chess_notation(self):
        return (self.get_rank_file(self.start_row, self.start_column) + 
                self.get_rank_file(self.end_row, self.end_column))
    
    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]
    


