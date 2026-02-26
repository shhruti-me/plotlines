from db import get_session

# =====================================================
# Recommendation Configuration
# =====================================================

WEIGHTS = {
    "actor": 0.35,
    "director": 0.30,
    "genre": 0.15,
    "keyword": 0.10,
    "dislike": 0.25,
    "popularity": 0.05,
}


# =====================================================
# Recommendation Engine
# =====================================================

def recommend_movies(user_id: str, limit: int = 10):
    """
    Hybrid graph-based recommendation engine.

    Combines:
    - User preference weights (actor, director, genre, keyword)
    - Genre dislike penalties
    - Popularity smoothing using log-scaled vote count

    Returns:
        List of (movie_title, score)
    """

    query = f"""
    MATCH (u:User {{userId: $userId}})

    // Candidate movies
    MATCH (m:Movie)
    WHERE NOT (u)-[:LIKED|DISLIKED]->(m)

    // Actor preference
    OPTIONAL MATCH (u)-[ua:LIKES_ACTOR]->(a:Actor)
    OPTIONAL MATCH (a)-[:ACTED_IN]->(m)
    OPTIONAL MATCH (m)-[:ACTED_IN]->(a)

    // Director preference
    OPTIONAL MATCH (u)-[ud:LIKES_DIRECTOR]->(d:Director)
    OPTIONAL MATCH (d)-[:DIRECTED]->(m)
    OPTIONAL MATCH (m)-[:DIRECTED]->(d)

    // Genre preference
    OPTIONAL MATCH (u)-[ug:LIKES_GENRE]->(g:Genre)<-[:HAS_GENRE]-(m)
    OPTIONAL MATCH (u)-[dg:DISLIKES_GENRE]->(g:Genre)<-[:HAS_GENRE]-(m)

    // Keyword preference
    OPTIONAL MATCH (u)-[uk:LIKES_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(m)

    WITH m,
         sum(coalesce(ua.weight, 0)) AS actorScore,
         sum(coalesce(ud.weight, 0)) AS directorScore,
         sum(coalesce(ug.weight, 0)) AS genreScore,
         sum(coalesce(dg.weight, 0)) AS dislikePenalty,
         sum(coalesce(uk.weight, 0)) AS keywordScore,
         coalesce(m.voteCount, 0)    AS voteCount

    WITH m,
         (actorScore    * {WEIGHTS["actor"]}) +
         (directorScore * {WEIGHTS["director"]}) +
         (genreScore    * {WEIGHTS["genre"]}) +
         (keywordScore  * {WEIGHTS["keyword"]}) +
         (dislikePenalty * {WEIGHTS["dislike"]}) +
         (log10(voteCount + 1) * {WEIGHTS["popularity"]}) AS score

    RETURN
        m.title AS title,
        score
    ORDER BY score DESC
    LIMIT $limit
    """

    with get_session() as session:
        result = session.run(
            query,
            userId=user_id,
            limit=limit
        )

        return [
            (record["title"], round(record["score"], 4))
            for record in result
        ]


# =====================================================
# Manual Test
# =====================================================

if __name__ == "__main__":
    test_user = "vstest"
    recommendations = recommend_movies(test_user)

    for title, score in recommendations:
        print(f"{title} -> {score}")