import os
from neo4j import GraphDatabase

# =====================================================
# Neo4j Configuration (Environment-Based)
# =====================================================

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", None)

# =====================================================
# Global Driver (Singleton)
# =====================================================

_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
    max_connection_lifetime=3600,
    max_connection_pool_size=10,
    connection_timeout=15,
)

# =====================================================
# Session Helper
# =====================================================

def get_session():
    """
    Returns a new Neo4j session.
    Used with 'with' context manager for safe auto-close.
    """
    if NEO4J_DATABASE:
        return _driver.session(database=NEO4J_DATABASE)
    return _driver.session()

# =====================================================
# Graceful Shutdown
# =====================================================

def close_driver():
    """
    Close the Neo4j driver cleanly.
    Call on FastAPI shutdown event.
    """
    _driver.close()