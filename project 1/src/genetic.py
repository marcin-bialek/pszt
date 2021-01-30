# Podstawy Sztucznej Inteligencji - przeszukiwanie
# Zadanie: Weselnicy 1
# Autor: Marcin Białek

import math
import random
import itertools
from data import Data
from config import Config
from chromosome import Chromosome


class Genetic():
    def __init__(self, config: Config, data: Data):
        self.config = config
        self.data = data 
        # Obliczenie maksymalnego poziomu zadowolenia 
        self.max_liking = self.data.people_per_table * (self.data.people_per_table - 1.0)


    # Główna pętla algorytmu genetycznego.
    def run(self, callback):
        self.avg_score = 1
        self.last_score = 1
        self.same_score_count = 0
        self.generation = 0
        self.population = self.initialize()
        self.evaluate(self.population)

        while True:
            # Obliczanie średniego wyniku w populacji 
            self.avg_score = sum(c.score for c in self.population) / len(self.population)

            callback(self.generation, self.avg_score)

            # Sprawdzenie, czy wynik się zmienił 
            if self.last_score == self.avg_score:
                self.same_score_count += 1

                # Koniec jeśli wynik nie zmienił się od 100 generacji 
                if self.same_score_count >= 100:
                    break
            else:
                self.last_score = self.avg_score
                self.same_score_count = 0

            # Operatory genetyczne
            parents = self.select(self.population)
            children = self.cross(parents)
            self.mutate(children)
            self.evaluate(children)
            self.population = self.succeed(self.population, children)
            self.generation += 1

        # Zwrócenie najlepszego chromosomu 
        return sorted(self.population, key = lambda c: c.score, reverse = True)[0]


    # Funkcja generująca początkowych osobników.
    def initialize(self):
        population = []

        for _ in range(self.config.population_size):
            # Tworzenie listy z numerami osób 
            people = list(range(self.data.num_of_people))
            # Permutacja listy
            random.shuffle(people)

            # Podział listy na równe części/stoły
            tables = []
            j = 0 
            while j < self.data.num_of_people:
                tables.append(people[j : j + self.data.people_per_table])
                j = j + self.data.people_per_table

            # Dodanie chromosomu do populacji 
            population.append(Chromosome(tables))

        return population


    # Funkcja oceniająca dopasowanie osobników.
    def evaluate(self, chromosomes):
        for chromosome in chromosomes:
            min_liking = float("inf")

            # Znajdowanie poziomu zadowolenia dla kadego stołu 
            for table in chromosome.tables:
                liking = float(0)
                
                # Suma poziomów sympatii osób przy stole 
                for (a, b) in itertools.permutations(table, 2):
                    liking += self.data.liking[a][b]

                if liking < min_liking:
                    min_liking = liking

            # Obliczanie wyniku dla chromosomu
            chromosome.score = 1.0 - (min_liking / self.max_liking)


    # Fukncja generująca pary (rodziców) z podanej grupy osobników.
    def select(self, chromosomes):
        parents = []
        probabilities = []
        total = sum(1 - c.score for c in chromosomes)

        # Przypisanie prawdopodobieństwa wyboru zgodnie z oceną 
        for chromosome in chromosomes:
            probabilities.append((1 - chromosome.score) / total)

        # Wybór par rodziców 
        for _ in range(self.config.population_size):
            pair = random.choices(chromosomes, probabilities, k = 2)
            parents.append(tuple(pair))

        return parents


    # Funkcja generująca nowych osobników na podstwie podanych par (rodziców). 
    def cross(self, parents):
        children = []

        for pair in parents:
            # Łączenie tablic z numerami osób 
            p1 = sum(pair[0].tables, [])
            p2 = sum(pair[1].tables, [])
            # Tworzenie tablicy dla dziecka 
            c = [-1] * len(p1)
            # Losowanie punktów rozcięć
            s = random.randrange(int(len(p1) / 2))
            e = random.randrange(int(len(p1) / 2), len(p1))
            # Przenoszenie części od rodzica 1 
            c[s:e] = p1[s:e]
            # Uzupełnianie brakujących osób od rodzica 2
            r = [x for x in p2 if x not in c]
            people = [x if x != -1 else r.pop(0) for x in c]

            # Podział tablicy na stoły i stworzenie chromosomu
            tables = []
            j = 0 
            while j < self.data.num_of_people:
                tables.append(people[j : j + self.data.people_per_table])
                j = j + self.data.people_per_table

            children.append(Chromosome(tables))

        return children


    # Fukncja wprowadzająca losowe mutacje w osobnikach.
    def mutate(self, chromosomes):
        for chromosome in chromosomes:
            if random.random() < self.config.mutation_rate:
                # Wylosowanie stołów 
                t1 = random.randrange(self.data.num_of_tables)
                t2 = random.randrange(self.data.num_of_tables)
                
                if t1 != t2:
                    # Wylosowanie pozycji przy stole 
                    p1 = random.randrange(self.data.people_per_table)
                    p2 = random.randrange(self.data.people_per_table)
                    # Zamiana osób 
                    p = chromosome.tables[t1][p1]
                    chromosome.tables[t1][p1] = chromosome.tables[t2][p2]
                    chromosome.tables[t2][p2] = p


    # Funkcja generująca nową populację na podstawie starych i nowych osobników.
    def succeed(self, old, new):
        # Sortowanie wszystkich chromosomów ze względu na ocenę 
        all_sorted = sorted(old + new, key = lambda c: c.score)
        # Zwrócenie najlepszych osobników 
        return all_sorted[0 : self.config.population_size]

