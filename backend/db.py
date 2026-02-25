from neo4j import GraphDatabase

# ---------------------------
# Neo4j Configuration
# ---------------------------
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

# ---------------------------
# Global Driver (singleton)
# ---------------------------
_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
    max_connection_lifetime=3600,
    max_connection_pool_size=10,
    connection_timeout=15,
)

# ---------------------------
# Session helper
# ---------------------------
def get_session():
    """
    Returns a new Neo4j session.
    Caller is responsible for closing it.
    """
    return _driver.session()

# ---------------------------
# Graceful shutdown
# ---------------------------
def close_driver():
    """
    Close the Neo4j driver cleanly.
    Call this on app shutdown if needed.
    """
    _driver.close()
