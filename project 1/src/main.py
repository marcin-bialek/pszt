#!/usr/bin/python3

# Podstawy Sztucznej Inteligencji - przeszukiwanie
# Zadanie: Weselnicy 1
# Autor: Marcin Białek

import sys
import csv
import json 
import getopt
import data 
import config
import genetic


# Wyświetlenie pomocy 
def print_help():
    print("Podstawy Sztucznej Inteligencji - przeszukiwanie")
    print("Program szukający optymalnego usadowienia osób przy stołach")
    print("na podstawie poziomów sympatii przy użyciu algorytmu genetycznego.")
    print("Autor: Marcin Białek\n")
    print("Opcje:")
    print("    -d [plik]   podanie pliku JSON z danymi (wymagane)\n")
    print("    -h          wyświetla pomoc")
    print("    -m M        prawdopodobieństwo mutacji, liczba z przedziału [0, 1]")
    print("                (domyślnie 0.1)")
    print("    -p P        rozmiar populacji, liczba naturalna (domyślnie 1000)")
    print("    -r [plik]   zapis rozwiązania do pliku [plik] (domyślnie result.json)")
    print("    -s [plik]   zapis średnich wartości funkcji dopasowania")
    print("                do pliku [plik]")
    print("Format pliku JSON z danymi:")
    print("    {")
    print("        \"liczba_osob\": [liczba naturalna],")
    print("        \"liczba_stolow\": [liczba naturalna],")
    print("        \"poziomy_sympatii\": [dwuwymiarowa tablica liczb z przedziału 0-1]")
    print("    }\n")


# Funkcja główna
def main(argv):
    arg_d = None
    arg_m = 0.1
    arg_p = 1000 
    arg_r = "result.json"
    arg_s = None 

    # Parsowanie opcji 
    try:
        opts, _ = getopt.getopt(argv, "d:hm:p:r:s:", []) 
    except getopt.GetoptError:
        print("pszt1.py [-hs] [-m num] [-p num] -d data.json")
        return 1

    # Obsługa opcji 
    for opt, arg in opts:
        if opt == "-h":
            print_help()
            return 0
        elif opt == "-d":
            arg_d = arg 
        elif opt == "-r":
            arg_r = arg 
        elif opt == "-s":
            arg_s = arg 
        elif opt == "-m":
            try:
                arg_m = float(arg)

                if arg_m < 0 or arg_m > 1:
                    raise Exception()
            except Exception:
                print("Błąd: prawdopodobieństwo mutacji musi być liczbą z przedziału [0, 1]")
                return 1
        elif opt == "-p":
            try:
                arg_p = int(arg)

                if arg_p < 1:
                    raise Exception()
            except Exception:
                print("Błąd: rozmiar populacji musi być liczbą naturalną")
                return 1

    # Sprawdzenie, czy został podany plik z danymi 
    if not arg_d:
        print("Błąd: nie został podany plik z danymi")
        return 1

    # Odczyt pliku z danymi 
    try:
        gen_data = data.from_json_file(arg_d)
    except data.DataError as ex:
        print("Błąd: %s" % (ex.msg,))
        return 1

    print("Liczba osób: %i" % gen_data.num_of_people)
    print("Liczba stołów: %i" % gen_data.num_of_tables)
    print("Rozmiar populacji: %i" % arg_p)
    print("Prawdopodobieństwo mutacji: %.2f" % arg_m)

    # Uruchomienie algorytmu 
    scores = []
    def callback(generation, avg_score):
        sys.stdout.write("\rGeneracja %i, średni wynik: %.3f   " % (generation, avg_score))
        sys.stdout.flush()
        scores.append((generation, round(avg_score, 4)))

    algorithm = genetic.Genetic(config.Config(arg_p, arg_m), gen_data)
    result = algorithm.run(callback)

    # Zapis wyniku do pliku 
    try:
        with open(arg_r, "w") as f:
            json.dump({ "stoly": result.tables }, f, indent = 4)
            print("\nWynik zapisano do pliku %s" % (arg_r,))
    except IOError as e:
        print("Błąd: nie udało się zapisać wyniku do pliku %s: %s" % (arg_r, e.strerror,))
        return 1

    if arg_s:
        # Zapis średnich wartości funkcji dopasowania do pliku
        try:
            with open(arg_s, "w") as f:
                file = csv.writer(f, delimiter = ";") 
                file.writerow(("generacja", "sredni_wynik"))
                file.writerows(scores)
                print("Średnie wartości funkcji dopasowania zapisano do pliku %s" % (arg_s,))
        except IOError as e:
            print("Błąd: nie udało się zapisać średnich wartości funkcji")
            print("dopasowania do pliku %s: %s" % (arg_s, e.strerror,))
            return 1

    return 0


if __name__ == "__main__":
    exit(main(sys.argv[1:]))

