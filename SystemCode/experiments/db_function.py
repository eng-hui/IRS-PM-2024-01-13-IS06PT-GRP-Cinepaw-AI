import sqlite3
import pandas as pd


# Connect to the database
conn = sqlite3.connect('movies.db')

def get_movie_details(movie_id):
    query = "SELECT * FROM movies WHERE movieId = (?)"
    movie_df = pd.read_sql(query, conn, params=(movie_id,))
    movie_name = movie_df['title'].values[0]
    genres = movie_df['genres'].values[0]    
    return movie_name,genres

# Test run of get_movie_details function
movie_id = 2
details = get_movie_details(movie_id)
print(details)
