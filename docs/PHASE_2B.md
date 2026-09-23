# P01 Phase 2b — Hybrid merge (TF-IDF + Pinecone)

**Status:** starting — after phase 2a smoke query confirmed.

**Surface:** Python scripts only (no FastAPI).

## Goal

For the same question (running example: `"What is step therapy?"`):

1. Get ranked hits from **TF-IDF** (keyword leg — `02_tfidf_search.py` logic).  
2. Get ranked hits from **Pinecone** (vector leg — already in `03`).  
3. **Merge** into one ranked list of `chunk_id`s (simple score mix or RRF — teach simple first).

```text
Question
  -> TF-IDF top_k
  -> Pinecone top_k
  -> merge
  -> final C00xx list (still no LLM answer yet — that is phase 3)
```

## Coaching depth (mandatory)

Same as phase 2a: **`next` / `what next` / `explain`** get **detailed line-by-line** teaching (what / why / pieces / memory picture). Few lines per turn. See [../BUILD_GUIDE.md](../BUILD_GUIDE.md).

## Planned script

`scripts/04_hybrid_search.py` (name may vary) — reuse load/retrieve helpers; do not paste a whole file at once in chat.

## Done when

One CLI run prints merged ranks for `"What is step therapy?"` with stable `chunk_id`s from both legs.
