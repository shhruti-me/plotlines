from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nlp_preferences import extract_preferences, store_text_preferences
from user_actions import (
    verify_or_create_user,
    like_movie,
    dislike_movie,
)
from recommend import recommend_movies

# ---------------------------
# App setup
# ---------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Schemas
# ---------------------------
class UserRequest(BaseModel):
    username: str


class TextPreferenceRequest(BaseModel):
    username: str
    text: str


class MovieListRequest(BaseModel):
    username: str
    liked: list[str]
    disliked: list[str]


# ---------------------------
# Routes
# ---------------------------

@app.post("/user/verify")
def verify_user(data: UserRequest):
    verify_or_create_user(data.username)
    return {
        "verified": True,
        "username": data.username,
    }


@app.post("/preferences/text")
def text_preferences(data: TextPreferenceRequest):
    print("TEXT PREF RECEIVED:", data.username, data.text)

    # Ensure user exists
    verify_or_create_user(data.username)

    # NLP → graph
    prefs = extract_preferences(data.text)
    store_text_preferences(data.username, prefs)

    # Recommend
    recommendations = recommend_movies(data.username)

    return {
        "recommendations": recommendations
    }


@app.post("/preferences/list")
def list_preferences(data: MovieListRequest):
    print("LIST PREF RECEIVED:", data.username, data.liked, data.disliked)

    # Ensure user exists
    verify_or_create_user(data.username)

    # Persist likes
    for movie in data.liked:
        like_movie(data.username, movie)

    # Persist dislikes
    for movie in data.disliked:
        dislike_movie(data.username, movie)

    # Recommend
    recommendations = recommend_movies(data.username)

    return {
        "recommendations": recommendations
    }
