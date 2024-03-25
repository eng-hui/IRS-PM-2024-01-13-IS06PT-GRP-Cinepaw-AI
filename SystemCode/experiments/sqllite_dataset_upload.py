import sqlite3
import pandas as pd
from sqlite3 import Error

#load csv files
movies_df = pd.read_csv('movies.csv')
ratings_df = pd.read_csv('ratings.csv')
links_df = pd.read_csv('links.csv')
tags_df = pd.read_csv('tags.csv')
genome_scores_df = pd.read_csv('genome-scores.csv')
genome_tags_df = pd.read_csv('genome-tags.csv')

#connection to SQLlite database
conn = sqlite3.connect('movies.db')
c = conn.cursor()

#load csv files to SQLlite
movies_df.to_sql('movies', conn,if_exists ='replace')
ratings_df.to_sql('ratings', conn,if_exists ='replace')
links_df.to_sql('links', conn,if_exists ='replace')
tags_df.to_sql('tags', conn,if_exists ='replace')
genome_scores_df.to_sql('genome_scores', conn,if_exists ='replace')
genome_tags_df.to_sql('genome_tags', conn,if_exists ='replace')


# c.execute("""CREATE TABLE movies (
#     movieId INTEGER PRIMARY KEY,
#     title TEXT,
#     genres TEXT
# )""")

# conn.commit()
# conn.close()