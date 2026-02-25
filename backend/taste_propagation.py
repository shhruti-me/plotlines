# backend/taste_propagation.py
from db import get_session
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"


def propagate_taste(user_id: str):
    """
    Propagate user taste from liked movies to actors, directors, and keywords.
    This function is SAFE to import in FastAPI.
    """

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    queries = [
        # Actors
        """
        MATCH (u:User {userId: $userId})-[r:LIKED]->(m:Movie)<-[aRel:ACTED_IN]-(a:Actor)
        WITH u, a,
             CASE WHEN aRel.order <= 2 THEN 0.6 ELSE 0.3 END * r.weight AS score
        MERGE (u)-[p:LIKES_ACTOR]->(a)
        SET p.weight = coalesce(p.weight, 0) + score
        """,

        # Directors
        """
        MATCH (u:User {userId: $userId})-[r:LIKED]->(m:Movie)<-[:DIRECTED]-(d:Director)
        WITH u, d, r.weight * 1.0 AS score
        MERGE (u)-[p:LIKES_DIRECTOR]->(d)
        SET p.weight = coalesce(p.weight, 0) + score
        """,

        # Keywords
        """
        MATCH (u:User {userId: $userId})-[r:LIKED]->(m:Movie)-[:HAS_KEYWORD]->(k:Keyword)
        WITH u, k, r.weight * 0.4 AS score
        MERGE (u)-[p:LIKES_KEYWORD]->(k)
        SET p.weight = coalesce(p.weight, 0) + score
        """
    ]

    with get_session() as session:
        for q in queries:
            session.run(q, userId=user_id)

    driver.close()
