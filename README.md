# governed-um-policy-rag

Policy knowledge retrieval for utilization management (UM) / benefits-style corpora: provenance on every chunk, ranked evidence with stable `chunk_id`s, and a path to hybrid search, grounded generation, and eval gates.

This is a small **enterprise retrieval slice**—audit-ready metadata, reproducible ingest, citation hooks—not a chatbot wrapper.

**Interface:** Python scripts / CLIs (no HTTP API in this repo).

## Stack

| Layer | Choice | Role |
|-------|--------|------|
| Corpus | Synthetic UM policy `.txt` | Safe public sample (no PHI) |
| Chunk catalog | JSONL + metadata | Stable `chunk_id` for citations |
| Keyword retrieval | **BM25** | Lexical / keyword hybrid leg |
| Embeddings | **Azure OpenAI** (`text-embedding-3-small`) | Dense representations |
| Vector index | **Pinecone** | Upsert by `chunk_id` + similarity query |
| Next | Hybrid merge → grounded answers | **BM25** + Pinecone, then Azure chat + evals |

Secrets stay in `.env` (see `.env.example`). Never commit keys.

## Architecture

```text
Corpus (.txt)
    -> chunk + metadata (source, classification, doc_type, chunk_id)
    -> keyword retriever  (BM25) [shipped]
    -> dense index        (Azure embed -> Pinecone) [shipped]
    -> hybrid merge       (BM25 + Pinecone, RRF)    [next]
    -> grounded answer    (Azure chat + citations)
    -> audit log + LLM-as-a-Judge CI
```

| Stage | Status |
|-------|--------|
| Ingest / provenance | Done |
| Keyword leg | **BM25 shipped** (CLI: `--query` / `--demo` / `--top-k`) |
| Azure embeddings + Pinecone upsert/query | Done |
| Hybrid fusion | Next (BM25 + Pinecone via RRF) |
| Grounded generation + judge CI | Planned |

## Implemented

- [x] Synthetic UM policy corpus → chunk catalog with metadata  
- [x] Stable `chunk_id`s for citation / audit  
- [x] **BM25** keyword CLI (enterprise lexical leg; `--query` / `--demo` / `--top-k`)  
- [x] Azure embeddings → Pinecone upsert + smoke query  
- [ ] Hybrid fusion (**BM25** + Pinecone via **RRF**)  
- [ ] **Cohere rerank** on fused shortlist  
- [ ] Azure answers with mandatory citations  
- [ ] Retrieval audit JSONL + metadata filters  
- [ ] Golden Q&A + judge threshold in CI  

## Run locally

```bash
python -m venv .venv
# Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env   # fill Azure + Pinecone values

python scripts/01_chunk_corpus.py
python scripts/02_bm25_search.py --query "What is step therapy?"
python scripts/03_pinecone_upsert.py
```

`03` embeds all chunks, upserts to Pinecone, then queries `"What is step therapy?"` and prints top `chunk_id`s.

Fresh clone: `data/chunks/` is not committed—run `01` before retrieval.

Setup notes: [docs/SETUP_AZURE.md](./docs/SETUP_AZURE.md) · [docs/SETUP_PINECONE.md](./docs/SETUP_PINECONE.md) · [docs/VERIFY_AZURE_PINECONE.md](./docs/VERIFY_AZURE_PINECONE.md)  
When to commit: [docs/COMMIT_AND_PUSH.md](./docs/COMMIT_AND_PUSH.md)

## Data

Synthetic policy text under `data/corpus/` only. No live payer data or PHI.

## Non-goals

- Not clinical decision support  
- Not HIPAA/SOC2 certification claims—governance **patterns** only  
- Not open-web RAG  

## License

Portfolio / interview use; swap in licensed corpora for production.
