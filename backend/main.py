from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

from db import close_driver, get_session
from nlp_preferences import extract_preferences, store_text_preferences
from user_actions import verify_or_create_user, like_movie, dislike_movie
from recommend import recommend_movies

# =====================================================
# Lifespan Handler
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_driver()

# =====================================================
# App Initialization
# =====================================================

app = FastAPI(
    title="Movie Recommendation API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# Request Schemas
# =====================================================

class UserRequest(BaseModel):
    username: str


class TextPreferenceRequest(BaseModel):
    username: str
    text: str


class MovieListRequest(BaseModel):
    username: str
    liked: List[str]
    disliked: List[str]

# =====================================================
# Routes
# =====================================================

@app.post("/user/verify")
def verify_user(data: UserRequest):
    verify_or_create_user(data.username)
    return {
        "verified": True,
        "username": data.username,
    }


@app.post("/preferences/text")
def text_preferences(data: TextPreferenceRequest):
    verify_or_create_user(data.username)

    preferences = extract_preferences(data.text)
    store_text_preferences(data.username, preferences)

    recommendations = recommend_movies(data.username)

    return {"recommendations": recommendations}


@app.post("/preferences/list")
def list_preferences(data: MovieListRequest):
    verify_or_create_user(data.username)

    for movie in data.liked:
        like_movie(data.username, movie)

    for movie in data.disliked:
        dislike_movie(data.username, movie)

    recommendations = recommend_movies(data.username)

    return {"recommendations": recommendations}


# =====================================================
# Movie Autocomplete Search (NEW)
# =====================================================
@app.get("/search")
def search_movies(q: str = Query(..., min_length=2)):
    with get_session() as session:
        result = session.run(
            """
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($q)
            RETURN id(m) AS id, m.title AS title, m.posterPath AS posterPath
            LIMIT 10
            """,
            q=q
        )

        movies = []

        for record in result:
            poster_path = record["posterPath"]
            movies.append({
                "id": record["id"],
                "title": record["title"],
                "poster": f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None
            })

        return movies