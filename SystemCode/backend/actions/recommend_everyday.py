from fastapi import FastAPI
import requests
from datetime import datetime
import random

app = FastAPI()
tmdb_api_key = "dfb7cec425423ead3c3d7a169d888d94" 

@app.get("/daily_popular_movie/")
async def daily_popular_movie():
    today = datetime.now()
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={tmdb_api_key}"
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])
    
    if not movies:
        return {"error": "No trending movies found"}
    
    # 热度排序
    movie = max(movies, key=lambda x: x['popularity'])
    return movie

@app.get("/theme_of_the_day/")
async def theme_of_the_day():
    theme = determine_daily_theme()
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&with_genres={theme}"
    response = requests.get(url)
    movies = response.json().get('results', [])
    
    if not movies:
        return {"error": "No movies found for today's theme"}
    
    movie = random.choice(movies)
    return movie

def determine_daily_theme():
    themes = {
        'Monday': '28',  # 动作
        'Tuesday': '12',  # 冒险
        'Wednesday': '16',  # 动画
        'Thursday': '35',  # 喜剧
        'Friday': '80',  # 犯罪
        'Saturday': '99',  # 纪录片
        'Sunday': '18',  # 剧情
    }
    weekday = datetime.now().strftime('%A')
    return themes[weekday]