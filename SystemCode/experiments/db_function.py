import sqlite3

# Connect to the database
conn = sqlite3.connect('movies.db')

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

    
def get_movie_details(movie_id):
    movie_title = get_movie_title(movie_id)
    genres = get_genres(movie_id)
    return movie_title, genres

# Test run of get_movie_details function
movie_id = 2
details = get_movie_details(movie_id)
print(details)
