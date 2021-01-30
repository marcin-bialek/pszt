#!/usr/bin/python3

# Podstawy Sztucznej Inteligencji - przeszukiwanie
# Zadanie: Weselnicy 1
# Autor: Marcin Białek

import sys
import getopt
import json 
import random 


def print_help():
    print("Program do generowania losowych danych dla programu pszt1.py.\n")
    print("Opcje:")
    print("    -h      wyświetla pomoc")
    print("    -n N    podanie liczby osób (wymagane)")
    print("    -m M    podanie liczby stołów (wymagane)")


# Funkcja główna
def main(argv):
    m = None 
    n = None 

    # Parsowanie opcji 
    try:
        opts, _ = getopt.getopt(argv, "hm:n:", []) 
    except getopt.GetoptError:
        print("gendata.py [-h] -m M -n N")
        return 1

    # Obsługa opcji 
    for opt, arg in opts:
        if opt == "-h":
            print_help()
            return 0
        elif opt == "-m":
            try:
                m = int(arg)
            except Exception:
                print("Błąd: M musi być liczbą naturalną") 
                print("Uruchom program z opcją -h, aby uzyskać pomoc.")
                return 1
        elif opt == "-n":
            try:
                n = int(arg)
            except Exception:
                print("Błąd: N musi być liczbą naturalną") 
                print("Uruchom program z opcją -h, aby uzyskać pomoc.")
                return 1

    if not m or not n:
        print("Błąd: nie podano N lub M") 
        print("Uruchom program z opcją -h, aby uzyskać pomoc.")
        return 1

    # Generowanie poziomów sympatii
    liking = []

    for i in range(n):
        p = [1 if i == j else round(random.random(), 4) for j in range(n)] 
        liking.append(p)

    # Tworzenie i zapis pliku z danymi
    data = {
        "liczba_osob": n,
        "liczba_stolow": m,
        "poziomy_sympatii": liking
    }

    try: 
        with open("data.json", "w") as f:
            json.dump(data, f, indent = 4)
            print("Dane zapisano do pliku data.json")
    except IOError as e:
        print("Błąd: nie udało się zapisać danych: %s" % (e.strerror,))
        return 1

    return 0


if __name__ == "__main__":
     exit(main(sys.argv[1:]))
