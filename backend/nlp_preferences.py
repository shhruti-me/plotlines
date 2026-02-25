import spacy
from db import get_session

# ---------------------------
# NLP model
# ---------------------------
nlp = spacy.load("en_core_web_sm")

# ---------------------------
# Controlled vocabularies
# ---------------------------
GENRES = {
    "action",
    "comedy",
    "drama",
    "thriller",
    "romance",
    "romantic",        # 👈 IMPORTANT synonym fix
    "science fiction",
    "sci-fi",
    "horror",
    "fantasy",
}

NEGATIONS = {"not", "don't", "dont", "hate", "dislike"}
POSITIVE_VERBS = {"like", "love", "enjoy", "prefer"}

# Normalize genre tokens
GENRE_NORMALIZATION = {
    "romantic": "Romance",
    "romance": "Romance",
    "sci-fi": "Science Fiction",
    "science fiction": "Science Fiction",
}


# ---------------------------
# Preference extraction
# ---------------------------
def extract_preferences(text: str) -> dict:
    doc = nlp(text.lower())

    liked_genres = set()
    disliked_genres = set()
    people = set()

    # Extract people (actors)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            people.add(ent.text.title())

    tokens = [t.text for t in doc]

    # Genre sentiment detection
    for i, token in enumerate(tokens):
        window = tokens[max(0, i - 3): i + 3]

        if token in GENRES:
            genre = GENRE_NORMALIZATION.get(token, token.title())

            if any(w in NEGATIONS for w in window):
                disliked_genres.add(genre)
            elif any(w in POSITIVE_VERBS for w in window):
                liked_genres.add(genre)

    return {
        "liked_genres": liked_genres,
        "disliked_genres": disliked_genres,
        "people": people,
    }


# ---------------------------
# Preference persistence
# ---------------------------
def store_text_preferences(username: str, prefs: dict) -> None:
    """
    Persist NLP-extracted preferences to Neo4j with weights.
    Guarantees user existence.
    """
    query = """
    MERGE (u:User {userId: $username})

    // Positive genre preferences
    FOREACH (g IN $liked_genres |
        MERGE (genre:Genre {name: g})
        MERGE (u)-[r:LIKES_GENRE]->(genre)
        SET r.weight = coalesce(r.weight, 0) + 0.8
    )

    // Negative genre preferences
    FOREACH (g IN $disliked_genres |
        MERGE (genre:Genre {name: g})
        MERGE (u)-[r:DISLIKES_GENRE]->(genre)
        SET r.weight = coalesce(r.weight, 0) - 0.8
    )

    // Actor preferences
    FOREACH (p IN $people |
        MERGE (a:Actor {name: p})
        MERGE (u)-[r:LIKES_ACTOR]->(a)
        SET r.weight = coalesce(r.weight, 0) + 1.0
    )
    """

    with get_session() as session:
        result = session.run(
            query,
            username=username,
            liked_genres=list(prefs["liked_genres"]),
            disliked_genres=list(prefs["disliked_genres"]),
            people=list(prefs["people"]),
        )

        # Force execution & visibility
        result.consume()


# ---------------------------
# Manual test
# ---------------------------
if __name__ == "__main__":
    user_id = "user_4"

    text = (
        "I love emotional romantic movies, "
        "but I don't like too much action. "
        "I enjoy Jamie Campbell Bower and Tom Hiddleston."
    )

    prefs = extract_preferences(text)
    print("EXTRACTED PREFS:", prefs)

    store_text_preferences(user_id, prefs)

    print("NLP preferences stored successfully.")
