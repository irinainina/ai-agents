import requests
import os
from dotenv import load_dotenv

load_dotenv()
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def search_unsplash_photos(query, per_page=2):
    if not UNSPLASH_ACCESS_KEY:
        print("Missing Unsplash access key.")
        return []

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "client_id": UNSPLASH_ACCESS_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [result["urls"]["regular"] for result in data.get("results", [])]
    except Exception as e:
        print(f"Unsplash error: {e}")
        return []
