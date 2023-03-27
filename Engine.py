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
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4) 
        self.checkmate = False
        self.stalemate = False 
        self.enpassant_possible = () #Współrzędne kwadratu gdzie bicie w przelocie jest dozwolone 
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs)]
    
    def make_move(self, move):
        """
        Funkcja bierze ruch jako parametr i wykonuje go (nie działa na roszadę, 
        promocję piona oraz bicie w przelocie)
        """
        self.board[move.start_row][move.start_column] = "--" #Pole, z którego ruszyła się figura staje się puste
        self.board[move.end_row][move.end_column] = move.piece_moved #Pole, na które ruszyła się figura
        self.move_log.append(move) #Zapisanie ruchu w historii
        self.white_to_move = not self.white_to_move #Gracze wykonują ruch na przemian
        if move.piece_moved == "wK": #Zmiana lokacji króla jeżeli wykona ruch
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == "bK": 
            self.black_king_location = (move.end_row, move.end_column)

        #Promocja piona
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + "Q"

        #Bicie w przelocie
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_column] = "--"
        #Jeżeli pion poruszy się o dwa pola możemy go zbić w przelocie
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_column)
        else:
            self.enpassant_possible = ()
        
        #Roszada
        if move.is_castle_move:
            if move.end_column - move.start_column == 2:  #Roszada po stronie króla
                self.board[move.end_row][move.end_column-1] = self.board[move.end_row][move.end_column+1]  #
                self.board[move.end_row][move.end_column+1] = '--'  #Usunięcie starej wieży
            else:  #Roszada po stronie królowej
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-2] 
                self.board[move.end_row][move.end_column-2] = '--' 
        #Zaktualizuj prawa do wykonania roszady po ruchu króla lub wieży 
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs))
    
    def undo_move(self):
        """Funkcja cofająca ruch"""
        if len(self.move_log) != 0: #Sprawdzenie czy w parti został wykonany jakikolwiek ruch
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move #Zmiana wykonawcy ruchu 
            if move.piece_moved == "wK": #Zmiana lokacji króla jeżeli cofniemy jego ruch
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == "bK": 
                self.black_king_location = (move.start_row, move.start_column)

            #Cofnięcie bicia w przelocie
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_column] = "--"  
                self.board[move.start_row][move.end_column] = move.piece_captured

            #Cofnięcie praw do roszady
            self.castle_rights_log.pop() #Usunięcie nowych praw do roszady po cofnięciu ruchu
            new_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastleRights(new_rights.wks, new_rights.bks, 
                                                       new_rights.wqs, new_rights.bqs)
            #Cofnięcie roszady
            if move.is_castle_move:
                if move.end_column - move.start_column == 2:  #Po stronie króla
                    self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-1]
                    self.board[move.end_row][move.end_column-1] = '--'
                else:  #Po stronie królowej
                    self.board[move.end_row][move.end_column-2] = self.board[move.end_row][move.end_column+1]
                    self.board[move.end_row][move.end_column+1] = '--'  

    def update_castle_rights(self, move):
        """Funkcja aktualizująca prawa do roszady po wykonaniu ruchu"""
        if move.piece_moved == "wK": #Po ruchu królem gracz traci prawo do wykonania roszady 
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_column == 0: #Lewa wieża
                    self.current_castling_right.wqs = False
                if move.start_column == 7: #Prawa wieża
                    self.current_castling_right.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_column == 0: #Lewa wieża
                    self.current_castling_right.bqs = False
                if move.start_column == 7: #Prawa wieża
                    self.current_castling_right.bks = False

    def get_valid_moves(self):
        """Wszystkie możliwe ruchy uwzględniające atak na króla(szach)"""
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_right.wks, #Skopiowanie aktualnych praw do roszady
        self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs)
        #1) Wygenerowanie wszystkich możliwych ruchów
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        #2) Dla każdego ruchu, wykonaj go
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
        #3) Wygenerowanie wszystkich możliwych ruchów przeciwnika
        #4) Sprawdzenie dla każdego ruchu przeciwnika czy zaatakował twojego króla
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i]) #5) Jeżeli zaatakują twojego króla, twój ruch jest niedozwolony
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0: #Gdy gracz nie może wykonać żadnego ruchu
            if self.in_check():
                self.checkmate = True #Gdy król jest szachowany następuje mat
            else:
                self.stalemate = True #Gdy król nie jest szachowany następuje pat
        else:
            self.checkmate = False
            self.stalemate = False 

        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_right = temp_castle_rights
        return moves
            
    def in_check(self):
        """Funkcja sprawdzająca czy w danej sytuacji król jest szachowany"""
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row, column):
        """Sprawdzenie czy figura przeciwnika atakuje dane pole"""
        self.white_to_move = not self.white_to_move #Zmiana na kolej ruchu przeciwnika
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move #Zmiana na kolej ruchu gracza 
        for move in opponent_moves:
            if move.end_row == row and move.end_column == column: #Pole jest atakowane
                return True 
        return False 
        
    def get_all_possible_moves(self):
        """Wszystkie możliwe ruchy nieuwzględniające ataku na króla(szach)"""
        moves = []
        for row in range(len(self.board)): #Ilość rzędów
            for column in range(len(self.board[row])): #Ilość kolumn w danym rzędzie
                turn = self.board[row][column][0] #Ustalanie, który gracz powinien wykonać teraz ruch
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
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
            if column - 1 >= 0: #Bicie w lewo
                if self.board[row-1][column-1][0] == "b": #Sprawdzenie czy stoi tam figura przeciwnika
                    moves.append(Move((row, column), (row-1,column-1), self.board))
                elif (row-1, column-1) == self.enpassant_possible: #Umożliwienia wykonania bicia w przelocie
                    moves.append(Move((row, column), (row-1,column-1), self.board, is_enpassant_move = True))

            if column + 1 <= 7: #Bicie w prawo
                if self.board[row-1][column+1][0] == "b":
                    moves.append(Move((row, column), (row-1,column+1), self.board))
                elif (row-1, column+1) == self.enpassant_possible:
                    moves.append(Move((row, column), (row-1,column+1), self.board, is_enpassant_move = True))

        else: #Ruchy czarnych pionów
            if self.board[row+1][column] == "--":
                moves.append(Move((row, column), (row+1, column), self.board))
                if row == 1 and self.board[row+2][column] == "--":
                    moves.append(Move((row, column), (row+2, column), self.board))
            if column - 1 >= 0:
                if self.board[row+1][column-1][0] == "w":
                    moves.append(Move((row, column), (row+1, column-1), self.board))
                elif (row+1, column-1) == self.enpassant_possible:
                    moves.append(Move((row, column), (row+1,column-1), self.board, is_enpassant_move = True))
            if column + 1 <= 7:
                if self.board[row+1][column+1][0] == "w":
                    moves.append(Move((row, column), (row+1, column+1), self.board))
                elif (row+1, column+1) == self.enpassant_possible:
                    moves.append(Move((row, column), (row+1,column+1), self.board, is_enpassant_move = True))

    def get_rook_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla wieży znajdującej się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
        #Ruchy białych i czarnych wież (nie wliczając bicia)
        ROOK_MOVES = [(0,1), (1,0), (-1,0), (0,-1)] #Zmiana współrzędnych po ruchu wieży
        enemy_piece_color = "b" if self.white_to_move else "w" #Sprawdzenie koloru bierek przeciwnika
        for move in ROOK_MOVES:
            for i in range(1,8):
                new_row = row + (move[0] * i)
                new_column = column + (move[1] * i)
                if 0 <= new_row <= 7 and 0 <= new_column <= 7:
                    if self.board[new_row][new_column] == "--":
                        moves.append(Move((row, column), (new_row, new_column), self.board))
                    elif self.board[new_row][new_column][0] != enemy_piece_color:
                        break
                    elif self.board[new_row][new_column][0] == enemy_piece_color:
                        moves.append(Move((row, column), (new_row, new_column), self.board))
                        break
                
    def get_knight_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla skoczka znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
        #Ruchy skoczków
        KNIGHT_MOVES = [(2,1), (1,2), (-1,2), (-2,1),
                    (-2,-1), (-1,-2), (1,-2), (2,-1)] #Zmiana współrzędnych po ruchu skoczka
        enemy_piece_color = "b" if self.white_to_move else "w" #Sprawdzenie koloru bierek przeciwnika
        for move in KNIGHT_MOVES:
            new_row = row + move[0]
            new_column = column + move[1]
            if 0 <= new_row <= 7 and 0 <= new_column <= 7:
                if (self.board[new_row][new_column] == "--" or 
                    self.board[new_row][new_column][0] == enemy_piece_color):
                    moves.append(Move((row, column), (new_row, new_column), self.board))
            
    def get_bishop_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla gońca znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
        #Ruchy białych i czarnych gońców (nie wliczając bicia)
        BISHOP_MOVES = [(1,1), (1,-1), (-1,1), (-1,-1)] #Zmiana współrzędnych po ruchu gońca
        enemy_piece_color = "b" if self.white_to_move else "w" #Sprawdzenie koloru bierek przeciwnika
        for move in BISHOP_MOVES:
            for i in range(1,8):
                new_row = row + (move[0] * i)
                new_column = column + (move[1] * i)
                if 0 <= new_row <= 7 and 0 <= new_column <= 7:
                    if self.board[new_row][new_column] == "--":
                        moves.append(Move((row, column), (new_row, new_column), self.board))
                    elif self.board[new_row][new_column][0] != enemy_piece_color:
                        break
                    elif self.board[new_row][new_column][0] == enemy_piece_color:
                        moves.append(Move((row, column), (new_row, new_column), self.board))
                        break

    def get_queen_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla królowej znajdującej się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

    def get_king_moves(self, row, column, moves):
        """
        Funkcja zwracająca wszystkie możliwe ruchy dla króla znajdującego się w konkretnym
        rzędzie oraz kolumnie i dodająca je do listy
        """
        KING_MOVES = [(0,1), (1,0), (-1,0), (0,-1),
                    (1,1), (-1,-1), (1,-1), (-1,1)] #Zmiana współrzędnych po ruchu króla
        enemy_piece_color = "b" if self.white_to_move else "w" #Sprawdzenie koloru bierek przeciwnika
        for move in KING_MOVES:
            new_row = row + move[0]
            new_column = column + move[1]
            if 0 <= new_row <= 7 and 0 <= new_column <= 7:
                if (self.board[new_row][new_column] == "--" or 
                    self.board[new_row][new_column][0] == enemy_piece_color):
                    moves.append(Move((row, column), (new_row, new_column), self.board))

    def get_castle_moves(self, row, column, moves):
        """Funkcja dodająca legalne ruchy roszady do listy ruchów króla"""
        if self.square_under_attack(row, column): #Nie możemy wykonać roszady podczas szachu
            return  
        if ((self.white_to_move and self.current_castling_right.wks) or 
        (not self.white_to_move and self.current_castling_right.bks)):
            self.get_king_side_castle_moves(row, column, moves)
        if (self.white_to_move and self.current_castling_right.wqs or 
        (not self.white_to_move and self.current_castling_right.bqs)):
            self.get_queen_side_castle_moves(row, column, moves)
        
    def get_king_side_castle_moves(self, row, column, moves):
        """Funkcja odpowiadająca za zwrócenie legalnych ruchów roszady po stronie króla"""
        if self.board[row][column+1] == "--" and self.board[row][column+2] == "--":
            if not self.square_under_attack(row, column+1) and not self.square_under_attack(row, column+2):
                moves.append(Move((row, column),(row,column+2), self.board, is_castle_move = True))

    def get_queen_side_castle_moves(self, row, column, moves): 
        """Funkcja odpowiadająca za zwrócenie legalnych ruchów roszady po stronie królowej"""
        if (self.board[row][column-1] == "--" and self.board[row][column-2] == "--" 
        and self.board[row][column-3] == "--"):
            if not self.square_under_attack(row, column-1) and not self.square_under_attack(row, column-2):
                moves.append(Move((row, column),(row,column-2), self.board, is_castle_move = True))


class CastleRights():
    """Klasa odpowiada za zdefiniowanie wszystkich możliwych 'typów' roszad"""
    def __init__(self, wks, bks, wqs, bqs): #wks = white king site, bqs = black queen site itd.
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs 


class Move:
    """Klasa ta odpowiada za wykonywanie ruchów"""
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()} #Zamiana współrzędnych listy na współrzędne
    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3, #szachowe np. ([0,3] = a5)
                    "e": 4, "f": 5, "g": 6, "h": 7} 
    columns_to_files = {v: k for k, v in files_to_columns.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False, is_castle_move = False):
        self.start_row = start_sq[0] #Współrzędne pola, z którego figura się rusza
        self.start_column = start_sq[1]
        self.end_row = end_sq[0] #Współrzędne pola, na które figura się rusza
        self.end_column = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column] #Przechowywanie zdobytych figur
        self.is_pawn_promotion = False 

        #Promocja piona
        if (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7):
            self.is_pawn_promotion = True #Sprawdzenie czy pion dotarł do ostatniego rzędu
        self.move_id = (self.start_row * 1000 + self.start_column * 100 + 
                        self.end_row * 10 + self.end_column) #Przypisanie ruchowi unikalnego id 
        
        #Bicie w przelocie
        self.is_enpassant_move = is_enpassant_move #Sprawdzenie czy bicie w przelocie jest dozwolone
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        #Roszada
        self.is_castle_move = is_castle_move

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


