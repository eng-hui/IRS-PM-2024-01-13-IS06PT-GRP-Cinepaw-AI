from fastapi import FastAPI, Query
from typing import List, Optional
import requests
app = FastAPI()

def google_search(query: str):
    api_key = "AIzaSyCh0jsJqWabIJZuvORkyr58hs35UJVBWFY"
    search_engine_id = "f085e9c16e1e040ee"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}"
    
    response = requests.get(search_url)
    search_results = response.json()
    return search_results.get("items", [])[:5]


@app.get("/search/")
async def search(query: Optional[str] = None):
    if query is None:
        return {"error": "Query parameter is required"}
    results = google_search(query)
    return {"results": results}

@app.get("/batch_search/")
async def batch_search(query_list: List[str] = Query([])):  # 使用默认值[]代替None
    batch_results = {}
    for query in query_list:
        batch_results[query] = google_search(query)
    return {"batch_results": batch_results}