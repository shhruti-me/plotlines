# Backend — Movie Recommender

Quick setup and run instructions for the Python backend.

Prerequisites
- Python 3.10+ recommended
- Neo4j database running and reachable

Setup

1. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Install the spaCy English model

```bash
python -m spacy download en_core_web_sm
```

4. Copy the example env and set credentials

```bash
copy .env.example .env
# then edit .env and set NEO4J_PASSWORD and any other values
```

5. Run the API

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Notes
- The backend expects a Neo4j instance seeded with movie nodes (see `preprocessing/`).
- Frontend runs separately (see `frontend/`).
