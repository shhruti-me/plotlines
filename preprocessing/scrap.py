import os
import requests
import pandas as pd
import time

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

if not API_KEY:
    raise RuntimeError("TMDB_API_KEY environment variable is required")

session = requests.Session()
session.headers.update({"accept": "application/json"})

movies_data = []
target_count = 10000
current_year = 2026

while len(movies_data) < target_count and current_year >= 1900:
    print(f"\nFetching year: {current_year}")

    for page in range(1, 501):

        if len(movies_data) >= target_count:
            break

        discover_url = (
            f"{BASE_URL}/discover/movie"
            f"?api_key={API_KEY}"
            f"&primary_release_year={current_year}"
            f"&page={page}"
        )

        try:
            response = session.get(discover_url, timeout=10)
            if response.status_code != 200:
                break

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for movie in results:

                if len(movies_data) >= target_count:
                    break

                movie_id = movie["id"]

                detail_url = (
                    f"{BASE_URL}/movie/{movie_id}"
                    f"?api_key={API_KEY}"
                    f"&append_to_response=keywords"
                )

                detail_response = session.get(detail_url, timeout=10)

                if detail_response.status_code == 200:
                    full_data = detail_response.json()
                    movies_data.append(full_data)
                    print("Fetched:", full_data.get("title"))

                time.sleep(0.3)

        except Exception as e:
            print("Error:", e)
            continue

    current_year -= 1

df = pd.DataFrame(movies_data)
df.to_csv("movies_10000.csv", index=False)

print("\nDone. Total movies collected:", len(df))