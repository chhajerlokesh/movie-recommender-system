import pandas as pd
import pickle

print("Python:", __import__("sys").executable)
print("Pandas:", pd.__version__)

movies = pd.read_csv("movies.csv")

with open("movies.pkl", "wb") as f:
    pickle.dump(movies, f)
