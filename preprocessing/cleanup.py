# cleanup.py

import pandas as pd
import ast

def preprocess():
    # ---------------------------
    # STEP 1: Load CSVs
    # ---------------------------
    movies = pd.read_csv("movies_metadata.csv", low_memory=False)
    credits = pd.read_csv("credits.csv")

    # ---------------------------
    # STEP 2: Fix and clean IDs
    # ---------------------------
    movies['id'] = pd.to_numeric(movies['id'], errors='coerce')
    movies = movies.dropna(subset=['id'])
    movies['id'] = movies['id'].astype(int)

    credits['movie_id'] = credits['movie_id'].astype(int)

    # ---------------------------
    # STEP 3: Merge datasets
    # ---------------------------
    df = movies.merge(
        credits,
        left_on="id",
        right_on="movie_id",
        how="inner"
    )

    # Drop duplicate title column
    if 'title_y' in df.columns:
        df.drop(columns=['title_y'], inplace=True)

    # ---------------------------
    # STEP 4: Parse JSON-like columns
    # ---------------------------
    def parse_json_column(val):
        if pd.isna(val):
            return []
        try:
            return ast.literal_eval(val)
        except:
            return []

    df['genres'] = df['genres'].apply(parse_json_column)
    df['keywords'] = df['keywords'].apply(parse_json_column)
    df['cast'] = df['cast'].apply(parse_json_column)
    df['crew'] = df['crew'].apply(parse_json_column)

    # ---------------------------
    # STEP 5: Clean Movie table
    # ---------------------------
    movies_clean = df[[
        'id',
        'title_x',
        'overview',
        'release_date',
        'runtime',
        'original_language',
        'popularity',
        'vote_average',
        'vote_count'
    ]].copy()

    movies_clean.rename(columns={
        'id': 'movieId',
        'title_x': 'title'
    }, inplace=True)

    movies_clean['releaseYear'] = pd.to_datetime(
        movies_clean['release_date'],
        errors='coerce'
    ).dt.year

    movies_clean.drop(columns=['release_date'], inplace=True)

    # ---------------------------
    # STEP 6: Actors + ACTED_IN
    # ---------------------------
    actor_rows = []
    acted_in_rows = []

    for _, row in df.iterrows():
        movie_id = row['id']
        for actor in row['cast']:
            actor_rows.append({
                "actorId": actor.get('id'),
                "name": actor.get('name')
            })
            acted_in_rows.append({
                "actorId": actor.get('id'),
                "movieId": movie_id,
                "order": actor.get('order', 99)
            })

    actors = pd.DataFrame(actor_rows).drop_duplicates()
    acted_in = pd.DataFrame(acted_in_rows)

    # ---------------------------
    # STEP 7: Directors + DIRECTED
    # ---------------------------
    director_rows = []
    directed_rows = []

    for _, row in df.iterrows():
        movie_id = row['id']
        for crew in row['crew']:
            if crew.get('job') == 'Director':
                director_rows.append({
                    "directorId": crew.get('id'),
                    "name": crew.get('name')
                })
                directed_rows.append({
                    "directorId": crew.get('id'),
                    "movieId": movie_id
                })

    directors = pd.DataFrame(director_rows).drop_duplicates()
    directed = pd.DataFrame(directed_rows)

    # ---------------------------
    # STEP 8: Genres + HAS_GENRE
    # ---------------------------
    genre_rows = []
    has_genre_rows = []

    for _, row in df.iterrows():
        movie_id = row['id']
        for genre in row['genres']:
            genre_rows.append({
                "genreId": genre.get('id'),
                "name": genre.get('name')
            })
            has_genre_rows.append({
                "movieId": movie_id,
                "genreId": genre.get('id')
            })

    genres = pd.DataFrame(genre_rows).drop_duplicates()
    has_genre = pd.DataFrame(has_genre_rows)

    # ---------------------------
    # STEP 9: Keywords + HAS_KEYWORD
    # ---------------------------
    keyword_rows = []
    has_keyword_rows = []

    for _, row in df.iterrows():
        movie_id = row['id']
        for kw in row['keywords']:
            keyword_rows.append({
                "keywordId": kw.get('id'),
                "name": kw.get('name')
            })
            has_keyword_rows.append({
                "movieId": movie_id,
                "keywordId": kw.get('id')
            })

    keywords = pd.DataFrame(keyword_rows).drop_duplicates()
    has_keyword = pd.DataFrame(has_keyword_rows)

    # ---------------------------
    # STEP 10: Languages + IN_LANGUAGE
    # ---------------------------
    languages = movies_clean[['original_language']] \
        .drop_duplicates() \
        .rename(columns={'original_language': 'code'})

    in_language = movies_clean[['movieId', 'original_language']] \
        .rename(columns={'original_language': 'code'})

    # ---------------------------
    # RETURN ALL DATA
    # ---------------------------
    return {
        "movies": movies_clean,
        "actors": actors,
        "directors": directors,
        "genres": genres,
        "keywords": keywords,
        "languages": languages,
        "acted_in": acted_in,
        "directed": directed,
        "has_genre": has_genre,
        "has_keyword": has_keyword,
        "in_language": in_language
    }


# ---------------------------
# Standalone run (debug only)
# ---------------------------
if __name__ == "__main__":
    data = preprocess()
    print("Preprocessing complete.")
    print("Movies:", data["movies"].shape)
    print("Actors:", data["actors"].shape)
    print("Directors:", data["directors"].shape)
    print("Genres:", data["genres"].shape)
    print("Keywords:", data["keywords"].shape)
