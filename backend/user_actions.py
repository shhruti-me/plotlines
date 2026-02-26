from datetime import datetime, timezone
from db import get_session
from taste_propagation import propagate_taste


# =====================================================
# User Management
# =====================================================

def verify_or_create_user(username: str) -> bool:
    """
    Ensure a User node exists.
    Safe and idempotent.
    """
    create_user(username)
    return True


def create_user(user_id: str) -> None:
    query = """
    MERGE (u:User {userId: $userId})
    """
    with get_session() as session:
        session.run(query, userId=user_id)


# =====================================================
# Movie Preference Actions
# =====================================================

def like_movie(user_id: str, movie_title: str, weight: float = 1.0) -> None:
    """
    Store positive movie preference.
    Triggers taste propagation.
    """
    query = """
    MATCH (u:User {userId: $userId})
    MERGE (m:Movie {title: $title})
    MERGE (u)-[r:LIKED]->(m)
    SET r.weight = $weight,
        r.timestamp = $timestamp
    """

    with get_session() as session:
        session.run(
            query,
            userId=user_id,
            title=movie_title,
            weight=weight,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # 🔥 Propagate taste after liking a movie
    propagate_taste(user_id)


def dislike_movie(user_id: str, movie_title: str, weight: float = -1.0) -> None:
    """
    Store negative movie preference.
    """
    query = """
    MATCH (u:User {userId: $userId})
    MERGE (m:Movie {title: $title})
    MERGE (u)-[r:DISLIKED]->(m)
    SET r.weight = $weight,
        r.timestamp = $timestamp
    """

    with get_session() as session:
        session.run(
            query,
            userId=user_id,
            title=movie_title,
            weight=weight,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# =====================================================
# Manual Test
# =====================================================

if __name__ == "__main__":
    user = "vstest"

    verify_or_create_user(user)

    like_movie(user, "Witchboard")
    like_movie(user, "The Twilight Saga: Breaking Dawn - Part 2", 0.8)
    like_movie(user, "The Mortal Instruments: City of Bones")
    dislike_movie(user, "Transformers")

    print("User movie preferences stored successfully.")