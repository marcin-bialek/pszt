#!/usr/bin/python3

# Podstawy Sztucznej Inteligencji
# Author: Marcin Białek

import sys
import csv
import ast
import math
import pathlib
import itertools
import numpy as np
from tensorflow.keras.utils import Sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow.keras.backend as K


DATA_DIR = "data"  # dir with files: https://www.kaggle.com/rounakbanik/the-movies-dataset
RESULTS_DIR = "results"
NEURONS_COUNTS = [ 16, 32, 64, 128 ]          
ACTIVATION_FUNCTIONS = [ "sigmoid", "tanh", "relu" ]    
DROPOUT_RATES = [ 0, 0.2, 0.5 ]         
REPEATS = 5


def parse_movie(row):
    return {
        "genres": [int(i["id"]) for i in ast.literal_eval(row["genres"])],
        "vote_average": float(row["vote_average"]),
        "casts": [],
        "keywords": []
    }


def get_casts(row):
    return [int(i["id"]) for i in ast.literal_eval(row["cast"])]


def get_keywords(row):
    return [int(i["id"]) for i in ast.literal_eval(row["keywords"])] 


def rmse(a, b):
    return K.sqrt(K.mean(K.square(a - b))) 


def main():
    pathlib.Path(RESULTS_DIR).mkdir(parents = True, exist_ok = True)
    movies = {}

    # Loading data

    print("Loading movies")

    with open(DATA_DIR + "/movies_metadata.csv") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if row["vote_count"] and int(row["vote_count"]) > 350:
                movies[int(row["id"])] = parse_movie(row)
            
    with open(DATA_DIR + "/credits.csv") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if int(row["id"]) in movies:
                movies[int(row["id"])]["casts"] = get_casts(row)

    with open(DATA_DIR + "/keywords.csv") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if int(row["id"]) in movies:
                movies[int(row["id"])]["keywords"] = get_keywords(row)

    # Encoding data 

    genres = set()
    casts = set()
    keywords = set()

    for m in movies.values():
        genres.update(m["genres"])
        casts.update(m["casts"])
        keywords.update(m["keywords"])

    genre_indices = { v: i for i, v in enumerate(genres) }
    casts_indices = { v: i + len(genre_indices) for i, v in enumerate(casts) }
    keywords_indices = { v: i + len(genre_indices) + len(casts_indices) for i, v in enumerate(keywords) }
    inputs_count = len(genre_indices) + len(casts_indices) + len(keywords_indices)
    data_x = np.zeros((len(movies), inputs_count))
    data_y = np.zeros((len(movies)))

    print("Encoding data")

    for i, m in enumerate(movies.values()):
        for id in m["casts"]:
            data_x[i, casts_indices[id]] = 1.0

        for id in m["genres"]:
            data_x[i, genre_indices[id]] = 1.0

        for id in m["keywords"]:
            data_x[i, keywords_indices[id]] = 1.0

        data_y[i] = m["vote_average"] / 10.0

    split = int(0.2 * data_x.shape[0])
    train_x = data_x[:-split]
    train_y = data_y[:-split]
    test_x = data_x[-split:]
    test_y = data_y[-split:]

    # Testing models with different params

    params = [p for p in itertools.product(NEURONS_COUNTS, ACTIVATION_FUNCTIONS, DROPOUT_RATES)]
    
    for p in params:
        results = []

        for i in range(0, REPEATS):
            print("Params: %i, %s, %.1f" % p)
            print("Iteration: %i" % (i + 1,))

            # Building a network

            model = Sequential()
            model.add(Dense(p[0], activation = p[1], kernel_initializer = 'normal'))

            if p[2] > 0:
                model.add(Dropout(p[2]))

            model.add(Dense(1, activation = "relu", kernel_initializer = 'normal'))
            model.compile(optimizer = "adam", loss = rmse)

            # Training and evaluating

            monitor = EarlyStopping(monitor = "val_loss", min_delta = 0.0001, patience = 100)
            history = model.fit(train_x, train_y, validation_data = (test_x, test_y), epochs = 50, batch_size = 16, callbacks = [monitor])
            results.append(history.history['loss'])
            results.append(history.history['val_loss'])

        # Saving results

        csv_rows = [sum((("loss_%i" % i, "val_loss_%i" % i) for i in range(0, REPEATS)), ("epoch",))]
        zipped = itertools.zip_longest(*results)
        csv_rows += [(i,) + r for i, r in enumerate(zipped)]

        with open(RESULTS_DIR + "/%i-%s-%.1f.csv" % p, "w") as file:
            writer = csv.writer(file)
            writer.writerows(csv_rows)


if __name__ == "__main__":
    main()

