#new
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from db import close_driver
from contextlib import asynccontextmanager

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
# App Initialization (ONLY ONCE)
# =====================================================

app = FastAPI(
    title="Movie Recommendation API",
    lifespan=lifespan
)

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