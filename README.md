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
| Generation | **Cohere / OpenAI** (`--backend` flag) | Grounded answer with mandatory source citations |
| Next | Access control, GraphRAG leg, audit + evals | Platform-agnostic |

Secrets stay in `.env` (see `.env.example`). Never commit keys.

## Architecture

```text
Corpus (.txt)
    -> chunk + metadata (source, classification, doc_type, chunk_id)
    -> keyword retriever  (BM25) [shipped]
    -> dense index        (Azure embed -> Pinecone) [shipped]
    -> hybrid merge       (BM25 + Pinecone, RRF)    [shipped]
    -> rerank             (Cohere rerank-v3.5)      [shipped]
    -> grounded answer    (Cohere/OpenAI + citations, --backend flag) [shipped]
    -> access control     (--role flag, chunk filtering, both retrieval legs) [shipped]
    -> GraphRAG leg       (--use-graph, toggleable 3rd retrieval leg) [next]
    -> audit log + LLM-as-a-Judge CI [next]
```

| Stage | Status |
|-------|--------|
| Ingest / provenance | Done |
| Keyword leg | **BM25 shipped** (CLI: `--query` / `--demo` / `--top-k`) |
| Azure embeddings + Pinecone upsert/query | Done |
| Hybrid fusion | **RRF merge shipped** (`04_hybrid_search.py`) |
| Cohere rerank | **Shipped** (`04_hybrid_search.py`, `rerank-v3.5`) |
| Grounded generation + citations | **Shipped** — dual backend (Cohere native citations + OpenAI manual citation parsing), `--backend {cohere,openai}` flag |
| Role-based access control | **Shipped** — `--role {adjuster,member}` flag; chunk-level `allowed_roles` filter applied before BM25, before Pinecone (native metadata `filter`), and before generation |
| GraphRAG toggle leg | Planned (`--use-graph` flag) |
| Audit log + judge CI | Planned |

## Implemented

- [x] Synthetic UM policy corpus → chunk catalog with metadata  
- [x] Stable `chunk_id`s for citation / audit  
- [x] **BM25** keyword CLI (enterprise lexical leg; `--query` / `--demo` / `--top-k`)  
- [x] Azure embeddings → Pinecone upsert + smoke query  
- [x] Hybrid fusion (**BM25** + Pinecone via **RRF**; `04_hybrid_search.py`)  
- [x] **Cohere rerank** on fused shortlist (`rerank-v3.5`, `04_hybrid_search.py`)  
- [x] Grounded generation with mandatory citations — **dual backend** (Cohere native `.citations` + OpenAI manual citation-tag parsing), selectable via `--backend {cohere,openai}`  
- [x] Role-based access control — `allowed_roles` on every chunk (data layer), `--role {adjuster,member}` CLI flag, filtered before BM25, before Pinecone (native metadata `filter`), and before generation; verified end-to-end (a `member` query for restricted audit-log content correctly returns "documents don't specify" rather than leaking it)  
- [ ] GraphRAG toggle leg (`--use-graph`, 3rd retrieval leg over policy cross-references). Build order: (1) NetworkX mechanics by hand (nodes, edges, neighbors) -> (2) hand-picked `CONCEPTS` loop over real chunks -> (3) Pydantic schema + Azure OpenAI structured-output extraction, run once at index time, saved to `data/graph/graph.json`, human-reviewed, `chunk_ids` kept on every node -> (4) graph leg feeds RRF, with the role filter applied to the graph leg too. No extra graph library  
- [ ] Retrieval audit JSONL + metadata filters  
- [ ] Golden Q&A + recall@k + DeepEval G-Eval judge threshold in CI (run per role)  
- [ ] **Production packaging, part 1:** `pyproject.toml` + lock file (uv) replacing `requirements.txt`  
- [ ] **Production packaging, part 2:** `Dockerfile` (multi-stage, non-root, secrets passed at run time, never baked into the image) + `compose.yaml`  
- [ ] **Production packaging, part 3:** GitHub Actions workflow YAML that runs the eval gate on every push and fails the build if scores drop  
- [ ] **Dependency supply-chain controls:** installs from the lock only (`uv sync --locked`, also in the Docker build), `uv audit` in the CI workflow, `.github/dependabot.yml` for `uv` and GitHub Actions; the managed-registry variant (Azure Artifacts) written up in `docs/adr/`. The local devpi mirror is built in the Docker-Compose project (P02)  
- [ ] **Logging:** replace `print` in the scripts with standard-library `logging` configured once in a shared helper (level from config, one timestamped format); modules use `logging.getLogger(__name__)`; command-line result output may stay as output, diagnostics go to logs; no secrets or raw personal data in log lines  
- [ ] **Eval analysis notebook (small):** `notebooks/eval_analysis.ipynb` loads the golden-set results and shows per-question recall@k, rerank scores and failures (which chunk was missed and why). Analysis only; the CI eval gate stays a script. Outputs cleared before commit  
- [ ] **Architecture + mentoring docs:** `docs/adr/` with 3-5 short Architecture Decision Records (seed: plain Python before a framework; BM25 + dense + RRF vs dense only; Cohere rerank; role filter on both legs) and `docs/ONBOARDING.md` (clone, configure, run, break something on purpose, fix it)  

**Status:** development paused; the open items above remain on the roadmap.  
**Progress: 8/18 checklist items done → 44%**

## Run locally

```bash
python -m venv .venv
# Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env   # fill Azure + Pinecone + Cohere + OpenAI values

python scripts/01_chunk_corpus.py
python scripts/02_bm25_search.py --query "What is step therapy?"
python scripts/03_pinecone_upsert.py
python scripts/04_hybrid_search.py --query "What is step therapy?"
python scripts/04_hybrid_search.py --query "What is step therapy?" --backend cohere
```

`03` embeds all chunks, upserts to Pinecone, then queries `"What is step therapy?"` and prints top `chunk_id`s.

`04` runs the BM25 leg and the Pinecone leg for the same query, fuses both rankings via Reciprocal Rank Fusion (RRF), reranks the fused shortlist with Cohere (`rerank-v3.5`), then generates a grounded answer with citations via either backend (`--backend openai`, the default, or `--backend cohere`) — only one generation API call happens per run. Sample real output for `"What is step therapy?"`:
```text
final: [('C0002', 0.598), ('C0001', 0.290), ('C0004', 0.016)]
openai_response.choices[0].message.content: Step therapy requires a trial of formulary-preferred alternative medications for a defined period before coverage of another medication, unless an exception applies. [C0002]
openai_citations ['C0002']
```

Access control example — same pipeline, `--role member` querying content that only exists in adjuster-only chunks:
```text
python scripts/04_hybrid_search.py --query "How are retrieval logs and audit records handled?" --role member --backend openai
Loaded 7 chunks ...           # 2 adjuster-only chunks excluded before BM25/Pinecone even run
final: [('C0008', 0.028), ('C0000', 0.012), ('C0002', 0.009)]
openai_response.choices[0].message.content: The provided documents do not specify how retrieval logs and audit records are handled. [C0000][C0002][C0008]
```
No leakage: the restricted chunks are filtered out of the local `chunks` list *and* excluded from Pinecone at query time via a native metadata `filter`, so they're never scored, retrieved, reranked, or seen by the LLM.

Fresh clone: `data/chunks/` is not committed—run `01` before retrieval.

Setup notes: [docs/SETUP_AZURE.md](./docs/SETUP_AZURE.md) · [docs/SETUP_PINECONE.md](./docs/SETUP_PINECONE.md) · [docs/VERIFY_AZURE_PINECONE.md](./docs/VERIFY_AZURE_PINECONE.md)

## Data

Synthetic policy text under `data/corpus/` only. No live payer data or PHI.

## Non-goals

- Not clinical decision support  
- Not HIPAA/SOC2 certification claims—governance **patterns** only  
- Not open-web RAG  

## License

Uses a synthetic corpus for demonstration; swap in licensed/production corpora before any real deployment.
