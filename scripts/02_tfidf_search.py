"""
P01 Phase 1: search chunks with TF-IDF (keyword retrieval).

Run from AgentForge root:
    python project_track/p01_rag_foundation/scripts/02_tfidf_search.py "What is step therapy?"
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

PROJECT_DIR = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_DIR / "data" / "chunks" / "chunks.jsonl"

TOP_K = 3

# print("chunks file exists:", CHUNKS_PATH.exists())
# print("TOP_K =", TOP_K)

def load_chunks(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows

# chunks = load_chunks(CHUNKS_PATH)
# print("loaded", len(chunks), "chunks")
# print("first id:", chunks[0]["chunk_id"])
# print("first text preview:", chunks[0]["text"][:80])

def retrieve(
    query: str,
    chunks: list[dict[str, str]],
    top_k: int = TOP_K,
) -> list[tuple[float, dict[str, str]]]:
    texts = [row["text"] for row in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    query_vec = vectorizer.transform([query])
    scores = linear_kernel(query_vec, matrix).flatten()
    ranked_indices = scores.argsort()[::-1][:top_k]
    return [(float(scores[i]), chunks[i]) for i in ranked_indices]

# chunks = load_chunks(CHUNKS_PATH)
# hits = retrieve("What is step therapy?", chunks, top_k=3)
# for score, row in hits:
#     print(score, row["chunk_id"], row["text"])

def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python 02_tfidf_search.py "your question here"')
    query = sys.argv[1]
    print("=== P01 Phase 1: TF-IDF search ===")
    print(f"Query: {query}")
    print()
    if not CHUNKS_PATH.exists():
        raise SystemExit(f"Missing {CHUNKS_PATH}. Run 01_chunk_corpus.py first.")
    chunks = load_chunks(CHUNKS_PATH)
    hits = retrieve(query, chunks, top_k=TOP_K)
    print(f"Top {TOP_K} chunks:")
    for rank, (score, row) in enumerate(hits, start=1):
        if(score <= 0):
            continue
        preview = row["text"][:120] + ("..." if len(row["text"]) > 120 else "")
        print(f"{rank}. score={score:.3f}  id={row['chunk_id']}  source={row['source']}")
        print(f"   {preview}")
        print()
    print("This is the RETRIEVE step of RAG. Later we GENERATE an answer from these chunks.")

if __name__ == "__main__":
    main()
    