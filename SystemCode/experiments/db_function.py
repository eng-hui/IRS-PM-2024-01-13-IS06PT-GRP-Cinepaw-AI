import sqlite3

# Connect to the database
conn = sqlite3.connect('movies.db')

# Input variables for the SQL query
movie_id = 2


# Create a cursor object
cursor = conn.cursor()

#get movie title from movie_id
def get_movie_title(movie_id):
    # Execute the SQL query with input variables
    cursor.execute("SELECT * FROM movies WHERE movieId = (?)", (movie_id,))

    # Fetch the row
    row = cursor.fetchone()

    # Check if a row is found
    if row:
        movie_title = row[2]
        return movie_title
    else:
        return None

# Get genres of a movie based on movie_id
def get_genres(movie_id):
    # Execute the SQL query with input variables
    cursor.execute("SELECT genres FROM movies WHERE movieId = (?)", (movie_id,))
    
    # Fetch the row
    row = cursor.fetchone()
    # Check if a row is found
    if row:
        genres = row[0]
        return genres
    else:
        return None


# Get relevance from movie id in table genome scores
def get_relevance(movie_id):
    # Execute the SQL query with input variables
    cursor.execute("SELECT relevance FROM genome_scores WHERE movieId = (?)", (movie_id,))

    # Fetch the row
    row = cursor.fetchone()

    # Check if a row is found
    if row:
        relevance = row[3]
        return relevance
    else:
        return None

# Get tag from movie id in table genome tags
def get_tag(movie_id):
    # Execute the SQL query with input variables
    cursor.execute("SELECT gt.tag FROM genome_tags gt LEFT JOIN genome_scores gs ON gt.tagId = gs.tagId WHERE gs.movieId = (?)", (movie_id,))

    # Fetch the row
    row = cursor.fetchone()

    # Check if a row is found
    if row:
        tag = row[2]
        return tag
    else:
        return None