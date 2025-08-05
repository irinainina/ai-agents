import os
import requests
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def search_pixabay_photos(keywords: list[str], per_page: int = 3) -> list[str]:
    base_url = "https://pixabay.com/api/"
    query_variants = [", ".join(keywords)]
    if keywords:
        query_variants.append(keywords[0])

    for query in query_variants:
        params = {
            "key": PIXABAY_API_KEY,
            "q": query,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": per_page
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            if hits:
                return [hit["webformatURL"] for hit in hits]

    return []
