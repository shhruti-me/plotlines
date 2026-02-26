# backend/taste_propagation.py

from db import get_session


def propagate_taste(user_id: str):
    """
    Propagate user taste from liked movies
    to actors, directors, and keywords.

    Converts:
        (User)-[:LIKED]->(Movie)
    into weighted preference edges like:
        (User)-[:LIKES_ACTOR]->(Actor)
        (User)-[:LIKES_DIRECTOR]->(Director)
        (User)-[:LIKES_KEYWORD]->(Keyword)
    """

    queries = [

        # =====================================================
        # Actor propagation
        # Top-billed actors weighted more
        # =====================================================
        """
        MATCH (u:User {userId: $userId})-[r:LIKED]->(m:Movie)<-[aRel:ACTED_IN]-(a:Actor)
        WITH u, a,
             CASE 
                 WHEN aRel.order <= 2 THEN 0.6 
                 ELSE 0.3 
             END * r.weight AS score
        MERGE (u)-[p:LIKES_ACTOR]->(a)
        SET p.weight = coalesce(p.weight, 0) + score
        """,

        # =====================================================
        # Director propagation
        # =====================================================
        """
        MATCH (u:User {userId: $userId})-[r:LIKED]->(m:Movie)<-[:DIRECTED]-(d:Director)
        WITH u, d, r.weight * 1.0 AS score
        MERGE (u)-[p:LIKES_DIRECTOR]->(d)
        SET p.weight = coalesce(p.weight, 0) + score
        """,

        # =====================================================
        # Keyword propagation
        # =====================================================
        """
        MATCH (u:User {userId: $userId})-[r:LIKED]->(m:Movie)-[:HAS_KEYWORD]->(k:Keyword)
        WITH u, k, r.weight * 0.4 AS score
        MERGE (u)-[p:LIKES_KEYWORD]->(k)
        SET p.weight = coalesce(p.weight, 0) + score
        """
    ]

    with get_session() as session:
        for query in queries:
            session.run(query, userId=user_id)