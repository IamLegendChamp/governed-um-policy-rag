"""
Build chunk catalog from policy corpus.

    python scripts/01_chunk_corpus.py           # health corpus only
    python scripts/01_chunk_corpus.py --dev    # + local teaching corpus_dev/
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
CORPUS_DIR = PROJECT_DIR / "data" / "corpus"
CORPUS_DEV_DIR = PROJECT_DIR / "data" / "corpus_dev"
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
    "rag_fundamentals.txt": {
        "industry": "cross",
        "classification": "internal",
        "doc_type": "engineering_reference",
    },
}


def banner(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def read_text_files(folders: list[Path]) -> list[tuple[str, str]]:
    documents: list[tuple[str, str]] = []
    for folder in folders:
        if not folder.exists():
            continue
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


def save_chunks_jsonl(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk policy corpus into chunks.jsonl.")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Also ingest data/corpus_dev/ (local teaching docs; gitignored).",
    )
    args = parser.parse_args()

    folders = [CORPUS_DIR]
    if args.dev:
        folders.append(CORPUS_DEV_DIR)

    banner("governed-um-policy-rag — chunk corpus")
    print(f"Folders      : {[str(f) for f in folders]}")
    print(f"Output file  : {CHUNKS_PATH}")
    print(f"dev_mode     : {args.dev}")

    documents = read_text_files(folders)
    if not documents:
        raise SystemExit(f"No .txt files in {folders}")

    banner("Step 1 - Documents found")
    for name, text in documents:
        print(f" • {name} ({len(text)} characters)")

    all_rows: list[dict[str, str]] = []
    chunk_id = 0
    banner("Step 2 - Chunking (preview)")
    for source, text in documents:
        pieces = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        meta = DOC_CATALOG.get(
            source,
            {"industry": "cross", "classification": "internal", "doc_type": "unknown"},
        )
        print(f"\n--- {source} -> {len(pieces)} chunks ---")
        for i, piece in enumerate(pieces):
            row = {
                "chunk_id": f"C{chunk_id:04d}",
                "source": source,
                "text": piece,
                **meta,
            }
            all_rows.append(row)
            if i < PREVIEW_CHUNKS_PER_DOC:
                print(f"    [{row['chunk_id']}] {piece[:90]}...")
            chunk_id += 1
        if len(pieces) > PREVIEW_CHUNKS_PER_DOC:
            hidden = len(pieces) - PREVIEW_CHUNKS_PER_DOC
            print(f"    ...+{hidden} more chunks (see chunks.jsonl)")

    save_chunks_jsonl(all_rows, CHUNKS_PATH)
    banner("Step 3 — Saved")
    print(f"Total chunks written: {len(all_rows)}")
    print(f"Open in editor: {CHUNKS_PATH}")
    banner("Step 4 — Sample record")
    print(json.dumps(all_rows[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
