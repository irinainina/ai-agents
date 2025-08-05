import os
import requests
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def search_pixabay_photos(keywords: list[str], per_page: int = 5) -> list[str]:
    if not PIXABAY_API_KEY:
        print("Missing Pixabay API key.")
        return []

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

        try:
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            hits = data.get("hits", [])
            if hits:
                return [hit["webformatURL"] for hit in hits]
        except Exception as e:
            print(f"Pixabay error ({query}): {e}")

    return []


def search_unsplash_photos(keywords: list[str], per_page: int = 5) -> list[str]:
    if not UNSPLASH_ACCESS_KEY:
        print("Missing Unsplash access key.")
        return []

    base_url = "https://api.unsplash.com/search/photos"
    query_variants = [", ".join(keywords)]
    if keywords:
        query_variants.append(keywords[0])

    for query in query_variants:
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape",
            "client_id": UNSPLASH_ACCESS_KEY,
        }

        try:
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if results:
                return [result["urls"]["regular"] for result in results]
        except Exception as e:
            print(f"Unsplash error ({query}): {e}")

    return []


def get_images(keywords: list[str], per_page: int = 5) -> list[str]:
    if not keywords:
        return []

    steps = [
      lambda: search_pixabay_photos(keywords, per_page),
      lambda: search_unsplash_photos(keywords, per_page),
      lambda: search_pixabay_photos([keywords[0]], per_page),
      lambda: search_unsplash_photos([keywords[0]], per_page),
  ]

    for step in steps:
        result = step()
        if result:
            return result

    return []
