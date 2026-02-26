import spacy
from db import get_session

# =====================================================
# NLP Model
# =====================================================

nlp = spacy.load("en_core_web_sm")

# =====================================================
# Configuration
# =====================================================

# Canonical genre mapping (handles synonyms + multi-word genres)
GENRE_MAP = {
    "action": "Action",
    "comedy": "Comedy",
    "drama": "Drama",
    "thriller": "Thriller",
    "romance": "Romance",
    "romantic": "Romance",
    "horror": "Horror",
    "fantasy": "Fantasy",
    "science fiction": "Science Fiction",
    "sci-fi": "Science Fiction",
}

NEGATIONS = {"not", "don't", "dont", "hate", "dislike"}
POSITIVE_VERBS = {"like", "love", "enjoy", "prefer"}

WINDOW_SIZE = 4  # Context window size for sentiment detection


# =====================================================
# Preference Extraction
# =====================================================

def extract_preferences(text: str) -> dict:
    """
    Extract:
    - Liked genres
    - Disliked genres
    - Actor names (PERSON entities)

    Uses phrase-level detection for multi-word genres.
    """

    doc = nlp(text.lower())
    full_text = doc.text

    liked_genres = set()
    disliked_genres = set()
    people = set()

    # ---------------------------
    # Extract actor names
    # ---------------------------
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            people.add(ent.text.title())

    tokens = [t.text for t in doc]

    # ---------------------------
    # Genre detection
    # ---------------------------
    for genre_phrase, canonical_name in GENRE_MAP.items():

        if genre_phrase in full_text:

            # Find token index of first occurrence
            for i, token in enumerate(tokens):

                # Match first word of phrase
                if token == genre_phrase.split()[0]:

                    # Build window
                    window = tokens[max(0, i - WINDOW_SIZE): i + WINDOW_SIZE]

                    if any(w in NEGATIONS for w in window):
                        disliked_genres.add(canonical_name)

                    elif any(w in POSITIVE_VERBS for w in window):
                        liked_genres.add(canonical_name)

    return {
        "liked_genres": liked_genres,
        "disliked_genres": disliked_genres,
        "people": people,
    }


# =====================================================
# Preference Persistence
# =====================================================

def store_text_preferences(username: str, prefs: dict) -> None:
    """
    Persist NLP-extracted preferences into Neo4j.

    - Likes increase weight
    - Dislikes decrease weight
    - Actor preferences strongly weighted
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

        # Force execution
        result.consume()


# =====================================================
# Manual Test
# =====================================================

if __name__ == "__main__":

    test_user = "vstest"

    sample_text = (
        "I love emotional romantic movies, "
        "but I don't like too much action. "
        "I enjoy Jamie Campbell Bower and Tom Hiddleston."
    )

    extracted = extract_preferences(sample_text)

    print("Extracted Preferences:")
    print(extracted)

    store_text_preferences(test_user, extracted)

    print("Preferences stored successfully.")