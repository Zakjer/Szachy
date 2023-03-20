# Szachy
Jest to klasyczna gra w szachy stworzona za pomocą języka Python przy użyciu biblioteki Pygame. Program pozwala grać dwóm graczom przeciwko sobie poprzez klikanie figur na interfejsie graficznym. Do gry zostały zaimplementowane standardowe zasady szachowe.

# Wymagania
Gra wymaga Pythona w wersji 3 oraz zainstalowanej biblioteki Pygame. Możesz zainstalować bibliotekę Pygame wpisując poniższe polecenie w konsoli.
```
pip install pygame
```

# Jak grać?
Aby rozpocząć grę, urochom plik main.py przy użyciu Pythona. Gdy program się uruchomi gracze mogą kliknąć na figurę, którą chcą się poruszyć a następnie kliknąć na kwadrat, na który chcą przenieść tę figurę. Jeżeli ruch jest dozwolony, gra uaktualni planszę, po czym nastąpi kolej na ruch drugiego gracza. Jeżeli ruch jest niedozwolony gracz będzie musiał wybrać inne pole lub figurę. Jeżeli gracze chcą cofnąć wykonany ruch można zrobić to przy użyciu klawisza "backspace" lub zresetować całkowity stan gry przy użyciu klawisza "r". 

# Pliki
**Main.py**: Jest to główny plik, który uruchamia program.

**Engine.py**: Plik ten zawiera logikę programu zaimplementowaną w klasach `StateOfTheGame` oraz `Move`.

**Pictures**: Folder ten zawiera zdjęcia wszystkich figur zapisanych w formacie .png.

**Sound_effects**: Folder ten zawiera efekty dźwiękowe, które są słyszane podczas konkretnych sytuacji podczas gry.

# Rzeczy do zrobienia
- dodanie dźwiękow go gry
- obracanie planszy po wykonaniu ruchu

https://github.com/Zakjer/Szachy
