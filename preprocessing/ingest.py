# ingest.py

from neo4j import GraphDatabase
from preprocessing.cleanup import preprocess

# ---------------------------
# Neo4j connection config
# ---------------------------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASSWORD:
    raise RuntimeError("NEO4J_PASSWORD environment variable is required for ingestion")

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# ---------------------------
# Load preprocessed data
# ---------------------------
data = preprocess()

movies_clean = data["movies"]
actors = data["actors"]
directors = data["directors"]
genres = data["genres"]
keywords = data["keywords"]
languages = data["languages"]
acted_in = data["acted_in"]
directed = data["directed"]
has_genre = data["has_genre"]
has_keyword = data["has_keyword"]
in_language = data["in_language"]

# ---------------------------
# Batch helpers
# ---------------------------
def batch_write(tx, query, rows):
    tx.run(query, rows=rows)

def write_in_batches(query, rows, batch_size=1000):
    with driver.session() as session:
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            session.execute_write(batch_write, query, batch)

# ---------------------------
# Create Movie nodes
# ---------------------------
movie_query = """
UNWIND $rows AS row
MERGE (m:Movie {movieId: row.movieId})
SET m.title = row.title,
    m.overview = row.overview,
    m.releaseYear = row.releaseYear,
    m.runtime = row.runtime,
    m.language = row.original_language,
    m.popularity = row.popularity,
    m.voteAverage = row.vote_average,
    m.voteCount = row.vote_count
"""
write_in_batches(movie_query, movies_clean.to_dict("records"))

# ---------------------------
# Actor nodes
# ---------------------------
actor_query = """
UNWIND $rows AS row
MERGE (a:Actor {actorId: row.actorId})
SET a.name = row.name
"""
write_in_batches(actor_query, actors.to_dict("records"))

# ---------------------------
# Director nodes
# ---------------------------
director_query = """
UNWIND $rows AS row
MERGE (d:Director {directorId: row.directorId})
SET d.name = row.name
"""
write_in_batches(director_query, directors.to_dict("records"))

# ---------------------------
# Genre nodes
# ---------------------------
genre_query = """
UNWIND $rows AS row
MERGE (g:Genre {genreId: row.genreId})
SET g.name = row.name
"""
write_in_batches(genre_query, genres.to_dict("records"))

# ---------------------------
# Keyword nodes
# ---------------------------
keyword_query = """
UNWIND $rows AS row
MERGE (k:Keyword {keywordId: row.keywordId})
SET k.name = row.name
"""
write_in_batches(keyword_query, keywords.to_dict("records"))

# ---------------------------
# Language nodes
# ---------------------------
language_query = """
UNWIND $rows AS row
MERGE (l:Language {code: row.code})
"""
write_in_batches(language_query, languages.to_dict("records"))

# ---------------------------
# ACTED_IN relationships
# ---------------------------
acted_in_query = """
UNWIND $rows AS row
MATCH (a:Actor {actorId: row.actorId})
MATCH (m:Movie {movieId: row.movieId})
MERGE (a)-[r:ACTED_IN]->(m)
SET r.order = row.order
"""
write_in_batches(acted_in_query, acted_in.to_dict("records"))

# ---------------------------
# DIRECTED relationships
# ---------------------------
directed_query = """
UNWIND $rows AS row
MATCH (d:Director {directorId: row.directorId})
MATCH (m:Movie {movieId: row.movieId})
MERGE (d)-[:DIRECTED]->(m)
"""
write_in_batches(directed_query, directed.to_dict("records"))

# ---------------------------
# HAS_GENRE relationships
# ---------------------------
has_genre_query = """
UNWIND $rows AS row
MATCH (m:Movie {movieId: row.movieId})
MATCH (g:Genre {genreId: row.genreId})
MERGE (m)-[:HAS_GENRE]->(g)
"""
write_in_batches(has_genre_query, has_genre.to_dict("records"))

# ---------------------------
# HAS_KEYWORD relationships
# ---------------------------
has_keyword_query = """
UNWIND $rows AS row
MATCH (m:Movie {movieId: row.movieId})
MATCH (k:Keyword {keywordId: row.keywordId})
MERGE (m)-[:HAS_KEYWORD]->(k)
"""
write_in_batches(has_keyword_query, has_keyword.to_dict("records"))

# ---------------------------
# IN_LANGUAGE relationships
# ---------------------------
language_rel_query = """
UNWIND $rows AS row
MATCH (m:Movie {movieId: row.movieId})
MATCH (l:Language {code: row.code})
MERGE (m)-[:IN_LANGUAGE]->(l)
"""
write_in_batches(language_rel_query, in_language.to_dict("records"))

# ---------------------------
# Done
# ---------------------------
driver.close()
print("Neo4j ingestion complete.")
