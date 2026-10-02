"""
Build the policy chunk catalog (JSONL) with provenance metadata.

    python scripts/01_chunk_corpus.py
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
CORPUS_DIR = PROJECT_DIR / "data" / "corpus"
CHUNKS_PATH = PROJECT_DIR / "data" / "chunks" / "chunks.jsonl"

CHUNK_SIZE = 280
CHUNK_OVERLAP = 60
PREVIEW_CHUNKS_PER_DOC = 3

DOC_CATALOG: dict[str, dict[str, str]] = {
    "utilization_management_policy.txt": {
        "industry": "health",
        "classification": "internal",
        "doc_type": "um_policy",
    },
}


def read_text_files(folder: Path) -> list[tuple[str, str]]:
    documents: list[tuple[str, str]] = []
    for path in sorted(folder.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        documents.append((path.name, text))
    return documents


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = start + chunk_size
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(cleaned):
            break
        start = end - overlap
    return chunks

def infer_allowed_roles(piece: str) -> list[str]:
    internal_keywords = ["Audit and retrieval", "Metadata for production"]
    is_internal = any(keyword in piece for keyword in internal_keywords)
    if is_internal:
        return ["adjuster"]
    return ["adjuster", "member"]

def save_chunks_jsonl(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    documents = read_text_files(CORPUS_DIR)
    if not documents:
        raise SystemExit(f"No .txt files in {CORPUS_DIR}")

    all_rows: list[dict[str, str]] = []
    chunk_id = 0
    for source, text in documents:
        pieces = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        meta = DOC_CATALOG.get(
            source,
            {"industry": "health", "classification": "internal", "doc_type": "unknown"},
        )
        for piece in pieces:
            row = {
                "chunk_id": f"C{chunk_id:04d}",
                "source": source,
                "text": piece,
                "allowed_roles": infer_allowed_roles(piece),
                **meta,
            }
            all_rows.append(row)
            chunk_id += 1

    save_chunks_jsonl(all_rows, CHUNKS_PATH)
    print(f"Wrote {len(all_rows)} chunks from {len(documents)} documents to {CHUNKS_PATH}")


if __name__ == "__main__":
    main()
