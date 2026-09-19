# governed-um-policy-rag

Internal **policy knowledge retrieval** for utilization management (UM) / benefits-style corpora: provenance on every chunk, ranked evidence with stable `chunk_id`s, and a roadmap to hybrid search, grounded generation, and eval gates.

Designed as an **enterprise retrieval slice** (audit-ready metadata, reproducible ingest, citation hooks)—not a chatbot wrapper.

## Architecture (target)

```text
Corpus (.txt)
    -> chunk + metadata (source, classification, doc_type, chunk_id)
    -> keyword retriever  (baseline / hybrid leg)     [shipped]
    -> dense index        (Pinecone + Azure embeddings) [next]
    -> hybrid merge
    -> grounded answer    (Azure AI Foundry + citations)
    -> audit log + LLM-as-a-Judge CI
```

| Layer | Status | Technology |
|-------|--------|------------|
| Ingest / provenance | Done | Fixed-window chunking → JSONL catalog |
| Keyword leg | Done | TF-IDF (control baseline for hybrid) |
| Vector memory | Planned | Pinecone |
| Embeddings + generation | Planned | Azure AI Foundry |
| Indexing orchestration | Planned | LlamaIndex |
| Answer chain + judge | Planned | LangChain · LLM-as-a-Judge |
| Corrective loop | Planned | LangGraph (optional) |

**Why a keyword leg first:** production hybrid RAG keeps a lexical path (codes, exact policy phrases) beside vectors. TF-IDF here is that **control surface**, not the end state.

## Implemented

- [x] Synthetic UM policy corpus → chunk catalog with metadata  
- [x] Stable `chunk_id`s for citation / audit  
- [x] Ranked retrieval CLI (lexical baseline)  
- [ ] Pinecone upsert + hybrid fusion  
- [ ] Azure Foundry answers with mandatory citations  
- [ ] Retrieval audit JSONL + metadata filters  
- [ ] Golden Q&A + judge threshold in CI  

## Run locally

```bash
python -m venv .venv
# Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt

# Build chunk catalog (required once, or after corpus / chunk settings change)
python scripts/01_chunk_corpus.py

# Lexical retrieval (operator CLI)
python scripts/02_tfidf_search.py --query "What is step therapy?"
python scripts/02_tfidf_search.py --query "When is prior authorization required?" --top-k 5

# UM smoke suite (config/demo_queries.yaml)
python scripts/02_tfidf_search.py --demo
```

Fresh clone: `data/chunks/` is not committed. Always run `01_chunk_corpus.py` before retrieval.

Secrets for later phases: copy `.env.example` → `.env` (never commit `.env`).

## Data

Synthetic policy text under `data/corpus/` only. No live payer data or PHI.

## Non-goals

- Not clinical decision support  
- Not HIPAA/SOC2 certification claims—governance **patterns** only  
- Not open-web RAG  

## License

Portfolio / interview use; swap in licensed corpora for production.
