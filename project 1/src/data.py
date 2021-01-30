# Podstawy Sztucznej Inteligencji - przeszukiwanie
# Zadanie: Weselnicy 1
# Autor: Marcin Białek

import json 


class DataError(Exception):
    def __init__(self, msg):
        self.msg = msg 


class Data():
    def __init__(self, num_of_people, num_of_tables, liking):
        if not isinstance(num_of_people, int) or not isinstance(num_of_tables, int):
            raise DataError("liczba_osob i liczba_stolow muszą być liczbami naturalnymi")
        if float(int(num_of_people/num_of_tables)) != num_of_people/num_of_tables:
            raise DataError("iloraz liczba_osob / liczba_stolow musi być liczbą naturalną")

        self.num_of_people = num_of_people
        self.num_of_tables = num_of_tables
        self.people_per_table = int(num_of_people/num_of_tables)
        self.liking = liking


def from_json_file(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as ex:
        raise DataError("%s: %s" % (path, ex.msg))
    except IOError:
        raise DataError("nie udało się otworzyć %s" % (path,))

    return Data(data["liczba_osob"], data["liczba_stolow"], data["poziomy_sympatii"])
