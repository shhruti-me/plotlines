import requests
import pandas as pd
import time
import os

API_KEY = "b31c1ec950e96a963102e80d0805c837" # Make sure this is set
BASE_URL = "https://api.themoviedb.org/3"

session = requests.Session()
session.headers.update({"accept": "application/json"})

# -------------------------------
# LOAD EXISTING DATA
# -------------------------------
existing_file = "movies_10000.csv"

if os.path.exists(existing_file):
    existing_df = pd.read_csv(existing_file)
    existing_ids = set(existing_df["id"].tolist())
    movies_data = existing_df.to_dict("records")
    print("Loaded existing movies:", len(existing_ids))
else:
    existing_ids = set()
    movies_data = []

target_count = 25000
current_year = 2026

while len(movies_data) < target_count and current_year >= 1995:

    print(f"\nFetching year: {current_year}")

    # First request to check total pages
    first_url = (
        f"{BASE_URL}/discover/movie"
        f"?api_key={API_KEY}"
        f"&primary_release_year={current_year}"
        f"&with_original_language=en"
        f"&sort_by=primary_release_date.desc"
        f"&page=1"
    )

    response = session.get(first_url, timeout=10)

    if response.status_code != 200:
        print("Failed year:", current_year)
        current_year -= 1
        continue

    data = response.json()
    total_pages = min(data.get("total_pages", 1), 500)

    for page in range(1, total_pages + 1):

        if len(movies_data) >= target_count:
            break

        discover_url = (
            f"{BASE_URL}/discover/movie"
            f"?api_key={API_KEY}"
            f"&primary_release_year={current_year}"
            f"&with_original_language=en"
            f"&vote_count.gte=20"
            f"&include_adult=false"
            f"&sort_by=primary_release_date.desc"
            f"&page={page}"
        )

        try:
            response = session.get(discover_url, timeout=10)
            if response.status_code != 200:
                break

            results = response.json().get("results", [])

            if not results:
                break

            for movie in results:

                movie_id = movie["id"]

                if movie_id in existing_ids:
                    continue

                detail_url = (
                    f"{BASE_URL}/movie/{movie_id}"
                    f"?api_key={API_KEY}"
                    f"&append_to_response=keywords"
                )

                detail_response = session.get(detail_url, timeout=10)

                if detail_response.status_code == 200:
                    full_data = detail_response.json()
                    movies_data.append(full_data)
                    existing_ids.add(movie_id)
                    print("Fetched:", full_data.get("title"))

                time.sleep(0.35)

        except Exception as e:
            print("Error:", e)
            continue

    current_year -= 1

df = pd.DataFrame(movies_data)
df.drop_duplicates(subset=["id"], inplace=True)

df.to_csv("movies_english_25000.csv", index=False)

print("\nDone.")
print("Total unique movies:", len(df))