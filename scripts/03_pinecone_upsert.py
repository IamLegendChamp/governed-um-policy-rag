"""
Embed policy chunks (Azure OpenAI) and upsert / smoke-query Pinecone (dense hybrid leg).

    python 03_pinecone_upsert.py

Requires: scripts/01_chunk_corpus.py already run, and .env with Azure + Pinecone keys.
Loads data/chunks/chunks.jsonl, embeds each chunk, upserts by chunk_id, then queries
"What is step therapy?" and prints top matches.
"""

from __future__ import annotations
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
import json
import os

PROJECT_DIR = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_DIR / "data" / "chunks" / "chunks.jsonl"

load_dotenv(PROJECT_DIR / ".env")

def load_chunks(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value or value == "replace-me":
        raise SystemExit(f"Missing or placeholder env vars: {name}")
    return value

def embed_text(client: AzureOpenAI, deployment: str, text: str) -> list[float]:
    response = client.embeddings.create(model=deployment, input=text)
    return list(response.data[0].embedding)

def get_pinecone_index():
    api_key = require_env("PINECONE_API_KEY")
    index_name = require_env("PINECONE_INDEX_NAME")
    pc = Pinecone(api_key=api_key)
    return pc.Index(index_name)

def main() -> None:
    if not CHUNKS_PATH.exists():
        raise SystemExit(f"Missing chunks. Run: python scripts/01_chunk_corpus.py")

    chunks = load_chunks(CHUNKS_PATH)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    endpoint = require_env("AZURE_OPENAI_ENDPOINT")
    api_key = require_env("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    deployment = require_env("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )

    sample = chunks[0]
    vector = embed_text(client, deployment, sample["text"])
    print(f"Sample embed ok: chunk_id={sample['chunk_id']} dim={len(vector)}")

    index = get_pinecone_index()
    print(f"Pinecone index open: {require_env('PINECONE_INDEX_NAME')}")

    records: list[dict] = []
    for row in chunks:
        vector = embed_text(client, deployment, row["text"])
        records.append(
            {
                "id": row["chunk_id"],
                "values": vector,
                "metadata": {
                    "source": row["source"],
                    "doc_type": row.get("doc_type", "unknown"),
                    "classification": row.get("classification", "internal")
                },
            }
        )

    index.upsert(vectors=records)
    print(f"Upserted {len(records)} vectors -> Pinecone")

    query = "What is step therapy?"
    query_vector = embed_text(client, deployment, query)

    result = index.query(vector=query_vector, top_k=3, include_metadata=True)
    print(f"Query: {query}")

    for rank, match in enumerate(result.matches, start=1):
        meta = match.metadata or {}
        print(
            f"{rank}. id={match.id} score={match.score:.3f} "
            f"doc_type={meta.get('doc_type', '?')} source={meta.get('source', '?')}"
        )

if __name__ == "__main__":
    main()

