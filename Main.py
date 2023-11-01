"""
To jest główny plik. Będzie on odpowiedzialny za obsługę informacji wprowadzonych przez użytkownika 
oraz za pobieranie danych z innych skryptów.
"""

import pygame as p 
from pygame import mixer
import os

from Engine import StateOfTheGame, Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH//DIMENSION
FPS = 25
IMAGES = {}

def load_images():
    """Funkcja ładująca obrazy figur w formacie .png"""
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wN", "wQ", "wK", "wB", "wR", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"Pictures/{piece}.png"), (SQ_SIZE, SQ_SIZE))

def main():
    """Funkcja główna pobiera input od użytkownika oraz na bieżąco aktualizuje wygląd szachownicy"""
    surface = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    p.display.set_caption("Chess")
    surface.fill(p.Color("white"))
    gs = StateOfTheGame() #Aktualny stan szachownicy 
    valid_moves = gs.get_valid_moves()
    move_made = False #Wartość po wykonaniu ruchu 
    animate = False 
    mixer.init() #Inicjalizacja miksera w celu puszczania efektów dźwiękowych
    p.font.init()
    load_images() #Funkcja wywyołana jednorazowo w celu załadowania obrazów
    running = True
    sq_selected = () #Monitorowanie kwadratu, w który kliknie użytkownik
    player_clicks = [] #Monitorowanie obu kliknięć użytkownika
    play_sound_effect("Game_start_sound")
    gameover = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            keys = p.key.get_pressed()
            if keys[p.K_ESCAPE]:
                running = False
            if keys[p.K_BACKSPACE]: #Cofnięcie ruchu po kliknięciu backspace
                gs.undo_move() 
                move_made = True
                animate = False
                gameover = False
            if keys[p.K_r]: #Resetowanie gry po kliknięciu klawisza r
                gs = StateOfTheGame()
                valid_moves = gs.get_valid_moves()
                sq_selected = ()
                player_clicks = []
                move_made = False
                animate = False 
                gameover = False
            elif e.type == p.MOUSEBUTTONDOWN: #Sprawdzenie, na który kwadrat kliknął użytkownik
                if not gameover:
                    location = p.mouse.get_pos() 
                    column = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, column): #Gdy użytkownik kliknie dwa razy na ten sam kwadrat
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, column)
                        player_clicks.append(sq_selected) #Dodanie do listy 1 i 2 kliknięcie użytkownika

                    if len(player_clicks) == 2: #Sprawdzenie czy użytkownik kliknął drugi raz (wykonał ruch)
                        move = Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]: #Sprawdzenie czy ruch jest poprawny
                                tymczasowe = player_clicks[1]
                                if gs.board[tymczasowe[0]][tymczasowe[1]] == "--":
                                    play_sound_effect("Move_sound")
                                else:
                                    play_sound_effect("Capture_sound")
                                #USPRAWNIC TE SEKCJE KODU I ROZWIAZAC PROBLEM KOLEJNOSCI IF STATEMENTOW
                                gs.make_move(valid_moves[i])
                                if gs.in_check():
                                    play_sound_effect("Check_sound")
                                print(move.get_chess_notation())
                                move_made = True 
                                animate = True
                                sq_selected = () #Zresetowanie kliknięcia użytkownika
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected] 

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], surface, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False 

        draw_game_state(surface, gs, valid_moves, sq_selected)
        #Rysowanie komunikatów po zakończeniu gry
        if gs.checkmate:
            gameover = True
            if gs.white_to_move:
                draw_text(surface, "Czarny wygrywa poprzez mata")
            else:
                draw_text(surface, "Biały wygrywa poprzez mata")
        elif gs.stalemate:
            gameover = True
            draw_text(surface, "Remis poprzez pata")

        clock.tick(FPS)
        p.display.flip()

def draw_game_state(surface, gs, valid_moves, sq_selected):
    """Funkcja odpowiedzialna za wyświetlenie obecnego stanu gry"""
    draw_board(surface)
    highlight_squares(surface, gs, valid_moves, sq_selected)
    draw_pieces(surface, gs.board)

def draw_board(surface):
    """Funkcja rysująca szachownicę"""
    global colors
    colors = [p.Color("white"), p.Color('gray')]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)] #Rysowanie białych oraz szarych kwadratów
            p.draw.rect(surface, color, p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(surface, board):
    """Funkcja odpowiedzialna za rysowanie figur w obecnym stanie gry"""
    for row in range(8):
        for column in range(8):
            piece = board[row][column]
            if piece != "--":
                surface.blit(IMAGES[piece], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(surface, gs, valid_moves, sq_selected):
    """Funkcja podświetlająca figurę oraz pola, na które może się poruszyć"""
    if sq_selected != ():
        row, column = sq_selected
        #Sprawdzenie czy możemy poruszyć się wybraną figurą
        if gs.board[row][column][0] == ("w" if gs.white_to_move else "b"):
            #Podświetlenie wybranej figury
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(70) #Wartość przezroczystości podświetlanego pola
            s.fill(p.Color("blue"))
            surface.blit(s, (column*SQ_SIZE, row*SQ_SIZE))
            #Podświetlenie pól, na które można się poruszyć
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    surface.blit(s, (move.end_column * SQ_SIZE, move.end_row * SQ_SIZE))

def animate_move(move, surface, board, clock):
    """Funkcja animująca ruch figury"""
    global colors 
    dR = move.end_row - move.start_row
    dC = move.end_column - move.start_column 
    frames_per_square = 3 #Ilość klatek ruchu na jednym polu
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        row = move.start_row + dR*frame/frame_count
        column = move.start_column + dC*frame/frame_count
        draw_board(surface)
        draw_pieces(surface, board)
        #Usunięcie figury z położenia końcowego
        color = colors[(move.end_row + move.end_column) % 2]
        end_square = p.Rect(move.end_column * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(surface, color, end_square)
        #Rysowanie zbitej figury
        if move.piece_captured != "--":
            surface.blit(IMAGES[move.piece_captured], end_square)
        #Rysowanie ruszonej figury
        surface.blit(IMAGES[move.piece_moved], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def play_sound_effect(effect_name):
    """Funkcja wywołująca efekt dźwiękowy"""
    sound_effect = p.mixer.Sound(os.path.join("Sound_effects", f"{effect_name}.mp3" ))
    p.mixer.Sound.play(sound_effect)

def draw_text(surface, text):
    """Funkcja wypisująca tekst na ekranie po zakończeniu gry"""
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color("Gray"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2,
                                                     HEIGHT/2 - text_object.get_height()/2)
    surface.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color("Black"))
    surface.blit(text_object, text_location.move(2, 2))
    
if __name__ == "__main__":
        main()
   

    