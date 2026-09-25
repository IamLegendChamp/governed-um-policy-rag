"""
BM25 keyword retrieval over the policy chunk catalog (lexical hybrid leg)
    python 02_bm25_search.py --query "What is step therapy?"
    python 02_bm25_search.py --demo 
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from rank_bm25 import BM25Okapi

import yaml

PROJECT_DIR = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_DIR / "data" / "chunks" / "chunks.jsonl"
DEMO_QUERIES_PATH = PROJECT_DIR / "config" / "demo_queries.yaml"
DEFAULT_TOP_K = 3

def load_chunks(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows

def tokenize(text: str) -> list[str]:
    return text.lower().split()

def retrieve(
    query: str,
    chunks: list[dict[str, str]],
    top_k: int = DEFAULT_TOP_K,
) -> list[tuple[float, dict[str, str]]]:
    tokenized_corpus = [tokenize(row["text"]) for row in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenize(query))
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [(float(scores[i]), chunks[i]) for i in ranked_indices]

def load_demo_queries(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        return list(cfg["queries"])

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank policy chunk for a query (BM25 keyword leg)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", "-q", type=str, help="Natural-language retrieval query.")
    group.add_argument(
        "--demo",
        action="store_true",
        help=f"Run smoke queries from {DEMO_QUERIES_PATH.relative_to(PROJECT_DIR)}.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Number of ranked chunks to return (default: {DEFAULT_TOP_K}).",
    )
    return parser

def main() -> None:
    args = build_parser().parse_args()

    if not CHUNKS_PATH.exists():
        raise SystemExit(f"Missing chunks. Run: python 01_chunk_corpus.py")

    chunks = load_chunks(CHUNKS_PATH)
    print(f"Loaded {len(chunks)} from {CHUNKS_PATH}")
    print(f"First chunk_id={chunks[0]['chunk_id']}")

    if args.demo:
        for item in load_demo_queries(DEMO_QUERIES_PATH):
            hits = retrieve(item["text"], chunks, top_k=args.top_k)
            print(f"Query: {item["text"]}")
            for rank, (score, row) in enumerate(hits, start=1):
                print(f"{rank}. score={score:.3f}  chunk_id={row['chunk_id']}")
            print()
        return

    hits = retrieve(args.query, chunks, top_k=args.top_k)
    print(f"Query: {args.query}")
    for rank, (score, row) in enumerate(hits, start=1):
        print(f"{rank}. score={score:.3f} chunk_id={row['chunk_id']}")

if __name__ == "__main__":
    main()