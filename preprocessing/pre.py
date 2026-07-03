import pandas as pd
import json

# =========================
# SAFE JSON PARSER
# =========================
def safe_json_load(val):
    if pd.isna(val) or val == "":
        return []
    try:
        return json.loads(val)
    except Exception:
        return []


# =========================
# LOAD RAW DATA
# =========================
movies_meta = pd.read_csv("movies_metadata.csv", low_memory=False)
credits_df = pd.read_csv("credits.csv", low_memory=False)

# =========================
# FIX & VALIDATE IDS
# =========================
movies_meta = movies_meta[pd.to_numeric(movies_meta["id"], errors="coerce").notnull()]
movies_meta["id"] = movies_meta["id"].astype(int)

if "movie_id" not in credits_df.columns:
    raise ValueError("credits.csv must contain a 'movie_id' column")

credits_df["movie_id"] = pd.to_numeric(
    credits_df["movie_id"], errors="coerce"
).astype("Int64")

credits_df = credits_df.dropna(subset=["movie_id"])
credits_df["movie_id"] = credits_df["movie_id"].astype(int)

# =========================
# MOVIES NODE CSV
# =========================
movies = movies_meta[
    ["id", "title", "overview", "release_date", "vote_average", "popularity"]
].dropna(subset=["id", "title"])

movies.to_csv("movies.csv", index=False)

# =========================
# GENRES + HAS_GENRE
# =========================
genre_nodes = []
has_genre = []

for _, row in movies_meta.iterrows():
    movie_id = row["id"]
    for g in safe_json_load(row.get("genres")):
        if "id" in g and "name" in g:
            genre_nodes.append({
                "genre_id": int(g["id"]),
                "name": g["name"]
            })
            has_genre.append({
                "movie_id": movie_id,
                "genre_id": int(g["id"])
            })

pd.DataFrame(genre_nodes).drop_duplicates().to_csv("genres.csv", index=False)
pd.DataFrame(has_genre).to_csv("has_genre.csv", index=False)

# =========================
# KEYWORDS + HAS_KEYWORD
# =========================
keyword_nodes = []
has_keyword = []

for _, row in movies_meta.iterrows():
    movie_id = row["id"]
    for k in safe_json_load(row.get("keywords")):
        if "id" in k and "name" in k:
            keyword_nodes.append({
                "keyword_id": int(k["id"]),
                "name": k["name"]
            })
            has_keyword.append({
                "movie_id": movie_id,
                "keyword_id": int(k["id"])
            })

pd.DataFrame(keyword_nodes).drop_duplicates().to_csv("keywords.csv", index=False)
pd.DataFrame(has_keyword).to_csv("has_keyword.csv", index=False)

# =========================
# PEOPLE + ACTED_IN + DIRECTED
# =========================
people_nodes = []
acted_in = []
directed = []

for _, row in credits_df.iterrows():
    movie_id = row["movie_id"]

    # CAST
    for c in safe_json_load(row.get("cast")):
        if "id" in c and "name" in c:
            pid = int(c["id"])
            people_nodes.append({
                "person_id": pid,
                "name": c["name"]
            })
            acted_in.append({
                "person_id": pid,
                "movie_id": movie_id,
                "character": c.get("character", "")
            })

    # CREW
    for c in safe_json_load(row.get("crew")):
        if "id" in c and "name" in c:
            pid = int(c["id"])
            people_nodes.append({
                "person_id": pid,
                "name": c["name"]
            })
            if c.get("job") == "Director":
                directed.append({
                    "person_id": pid,
                    "movie_id": movie_id
                })

pd.DataFrame(people_nodes).drop_duplicates().to_csv("people.csv", index=False)
pd.DataFrame(acted_in).to_csv("acted_in.csv", index=False)
pd.DataFrame(directed).to_csv("directed.csv", index=False)

# =========================
# FINAL CHECK
# =========================
print("FILES CREATED SUCCESSFULLY")
print("---------------------------")
print("Movies:", len(pd.read_csv("movies.csv")))
print("People:", len(pd.read_csv("people.csv")))
print("Genres:", len(pd.read_csv("genres.csv")))
print("Keywords:", len(pd.read_csv("keywords.csv")))
print("Acted In:", len(pd.read_csv("acted_in.csv")))
print("Directed:", len(pd.read_csv("directed.csv")))