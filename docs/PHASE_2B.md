# P01 Phase 2b — BM25 + hybrid merge (RRF) + Cohere rerank

**Status:** BM25 (2b-1) **done**. `02_tfidf_search.py` deleted. Starting 2b-2/2b-3 (`04_hybrid_search.py`).

**Surface:** Python scripts only (no FastAPI).

## In scope for P01 (required)

| Step | What | Script |
|------|------|--------|
| **2b-1** | **BM25** keyword leg (replaced TF-IDF) | `02_bm25_search.py` ✅ done — `retrieve()`, `--query`/`--demo`/`--top-k` CLI, verified against 3 demo queries |
| **2b-2** | Pinecone dense top_k (reuse `03` patterns) | inside `04` or helper — next |
| **2b-3** | **RRF** merge of BM25 + Pinecone ranks | `04_hybrid_search.py` — next |
| **2b-4** | **Cohere rerank** on fused shortlist | extend `04` or `05_rerank.py` |

```text
Question
  -> BM25 top_k
  -> Pinecone top_k
  -> RRF merge
  -> Cohere rerank (shortlist)
  -> final C00xx  (phase 3: grounded answer)
```

~~TF-IDF (`02_tfidf_search.py`) stays until BM25 CLI is solid~~ — **done.** BM25 CLI matched TF-IDF's `--query`/`--demo` UX with sensible ranks (verified: `"What is step therapy?"` → C0001/C0002/C0008; `"prior authorization"` → C0001/C0004; demo mode ran all 3 smoke queries correctly). `02_tfidf_search.py` deleted in the "Replace TF-IDF keyword leg with BM25" commit.

## Coaching

`next` / `explain` → detailed line-by-line. Few lines per turn.

**Main-first:** after the first helper (e.g. `load_chunks`), add a thin `main()` early so we can run and **print** proofs while `retrieve` / argparse grow. See [../BUILD_GUIDE.md](../BUILD_GUIDE.md).

## Done when

BM25 CLI works → RRF hybrid prints merged ids → Cohere rerank reorders the shortlist for `"What is step therapy?"`.
