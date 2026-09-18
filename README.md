# governed-um-policy-rag

Governed retrieval over **utilization management (UM) / benefits-style policy** text: chunked corpus with provenance metadata, keyword retrieval baseline, and a path to hybrid vector search with citation-ready `chunk_id`s.

Built for **enterprise knowledge retrieval** patterns (audit-oriented metadata, reproducible chunking, ranked evidence)—not a chat demo.

## Stack

| Layer | Choice |
|-------|--------|
| Keyword retrieval | TF-IDF (scikit-learn) |
| Vector memory (next) | Pinecone |
| Generation / embeddings (next) | Azure AI Foundry |
| Indexing framework (next) | LlamaIndex |
| RAG chain / evals (next) | LangChain · LLM-as-a-Judge |

## What’s implemented

- [x] Ingest synthetic UM + reference corpus → `data/chunks/chunks.jsonl`
- [x] Metadata on every chunk: `industry`, `classification`, `doc_type`, `source`, `chunk_id`
- [x] TF-IDF top-k retrieval CLI
- [ ] Pinecone upsert + hybrid merge
- [ ] Azure Foundry grounded answers with citations
- [ ] Retrieval audit log + metadata filters
- [ ] Golden Q&A + LLM-as-a-Judge gate

## Quick start

```bash
python -m venv .venv
# Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt

python scripts/01_chunk_corpus.py
python scripts/02_tfidf_search.py "What is step therapy?"
python scripts/02_tfidf_search.py "What is hybrid RAG?"
```

Copy `.env.example` → `.env` before Azure / Pinecone phases. **Never commit `.env`.**

## Corpus

Synthetic training text only (`data/corpus/`). No live payer or PHI data.

## Non-goals

- Not clinical decision support or diagnosis  
- Not a claim of HIPAA / SOC2 certification—governance **patterns** (ids, metadata, audit hooks)  
- Not open-web crawling  

## License

Use freely for portfolio / interview demos; replace corpus with your licensed content for production.
