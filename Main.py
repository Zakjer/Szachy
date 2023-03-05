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
FPS = 15
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
    surface.fill(p.Color("white"))
    mixer.init() #Inicjalizacja miksera w celu puszczania efektów dźwiękowych
    gs = StateOfTheGame() #Aktualny stan szachownicy 
    valid_moves = gs.get_valid_moves()
    move_made = False #Wartość po wykonaniu ruchu 
    load_images() #Funkcja wywyołana jednorazowo w celu załadowania obrazów
    running = True
    sq_selected = () #Monitorowanie kwadratu, w który kliknie użytkownik
    player_clicks = [] #Monitorowanie obu kliknięć użytkownika
    play_sound_effect("Game_start_sound")

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            keys = p.key.get_pressed()
            if keys[p.K_BACKSPACE]: #Cofnięcie ruchu po kliknięciu backspace
                gs.undo_move() 
                move_made = False 
            elif e.type == p.MOUSEBUTTONDOWN: #Sprawdzenie, na który kwadrat kliknął użytkownik
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
                    print(move.get_chess_notation())
                    if move in valid_moves: #Sprawdzenie czy ruch jest poprawny
                        gs.make_move(move)
                        play_sound_effect("Move_sound")
                        move_made = True 
                    sq_selected = () #Zresetowanie kliknięcia użytkownika
                    player_clicks = []

        if move_made:
            valid_moves = gs.get_valid_moves
            move_made = False

        draw_game_state(surface, gs)
        clock.tick(FPS)
        p.display.flip()

def draw_game_state(surface, gs):
    """Funkcja odpowiedzialna za wyświetlenie obecnego stanu gry"""
    draw_board(surface)
    draw_pieces(surface, gs.board)

def draw_board(surface):
    """Funkcja rysująca szachownicę"""
    colors = [p.Color("white"), p.Color("gray")]
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

def play_sound_effect(effect_name):
    """Funkcja wywołująca efekt dźwiękowy"""
    sound_effect = p.mixer.Sound(os.path.join("Sound_effects", f"{effect_name}.mp3" ))
    p.mixer.Sound.play(sound_effect)

if __name__ == "__main__":
    main()
    