"""
Lexical retrieval CLI over the policy chunk catalog (keyword leg of hybrid RAG).

    python scripts/02_tfidf_search.py --query "What is step therapy?"
    python scripts/02_tfidf_search.py --demo
    python scripts/02_tfidf_search.py --query "prior authorization" --top-k 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

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


def retrieve(
    query: str,
    chunks: list[dict[str, str]],
    top_k: int = DEFAULT_TOP_K,
) -> list[tuple[float, dict[str, str]]]:
    texts = [row["text"] for row in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    query_vec = vectorizer.transform([query])
    scores = linear_kernel(query_vec, matrix).flatten()
    ranked_indices = scores.argsort()[::-1][:top_k]
    return [(float(scores[i]), chunks[i]) for i in ranked_indices]


def load_demo_queries(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return list(cfg["queries"])


def print_hits(query: str, hits: list[tuple[float, dict[str, str]]], top_k: int) -> None:
    print("=== governed-um-policy-rag · lexical retrieval ===")
    print(f"query: {query}")
    print(f"top_k: {top_k}")
    print()
    shown = 0
    for rank, (score, row) in enumerate(hits, start=1):
        if score <= 0:
            continue
        shown += 1
        preview = row["text"][:120] + ("..." if len(row["text"]) > 120 else "")
        print(
            f"{rank}. score={score:.3f}  chunk_id={row['chunk_id']}  "
            f"source={row['source']}  doc_type={row.get('doc_type', '?')}"
        )
        print(f"   {preview}")
        print()
    if shown == 0:
        print("No positive-score hits.")
    print("retrieval_complete")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank policy chunks for a query (lexical / TF-IDF baseline)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--query",
        "-q",
        type=str,
        help="Natural-language retrieval query.",
    )
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
    parser.add_argument(
        "--chunks",
        type=Path,
        default=CHUNKS_PATH,
        help="Path to chunks.jsonl catalog.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.chunks.exists():
        raise SystemExit(
            f"Missing chunk catalog: {args.chunks}. Run: python scripts/01_chunk_corpus.py"
        )

    chunks = load_chunks(args.chunks)

    if args.demo:
        for item in load_demo_queries(DEMO_QUERIES_PATH):
            print(f"--- demo_id={item['id']} ---")
            hits = retrieve(item["text"], chunks, top_k=args.top_k)
            print_hits(item["text"], hits, args.top_k)
            print()
        return

    hits = retrieve(args.query, chunks, top_k=args.top_k)
    print_hits(args.query, hits, args.top_k)


if __name__ == "__main__":
    main()
