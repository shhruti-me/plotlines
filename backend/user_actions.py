from datetime import datetime, timezone
from db import get_session

# ---------------------------
# User management
# ---------------------------

def verify_or_create_user(username: str) -> bool:
    """
    Ensures a User node exists.
    Idempotent operation.
    """
    print("verifying or creating user:", username)
    create_user(username)
    return True


def create_user(user_id: str) -> None:
    query = """
    MERGE (u:User {userId: $userId})
    """
    with get_session() as session:
        session.run(query, userId=user_id)


# ---------------------------
# Movie preference actions
# ---------------------------

def like_movie(user_id: str, movie_title: str, weight: float = 1.0) -> None:
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


def dislike_movie(user_id: str, movie_title: str, weight: float = -1.0) -> None:
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


# ---------------------------
# Manual test
# ---------------------------
if __name__ == "__main__":
    user = "user_3"

    verify_or_create_user(user)

    like_movie(user, "Witchboard", 1.0)
    like_movie(user, "The Twilight Saga: Breaking Dawn - Part 2", 0.8)
    like_movie(user, "The Mortal Instruments: City of Bones", 1.0)
    dislike_movie(user, "Transformers", -1.0)

    print("User movie preferences stored successfully.")
