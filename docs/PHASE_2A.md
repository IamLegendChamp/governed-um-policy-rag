# P01 Phase 2a — Dense index (Azure embeddings + Pinecone)

**Status:** done — terminal confirmed upsert + smoke query (`C0002` top for `"What is step therapy?"`).

**Surface:** Python scripts only (no FastAPI).

## Goal

Load `data/chunks/chunks.jsonl` → embed each `text` with Azure → upsert into Pinecone by `chunk_id` → smoke query `"What is step therapy?"`.

## Coaching depth (mandatory)

When the learner says **`next`**, **`what next`**, or **`explain` / `line by line`**:

- Full per-line depth: what / why / each piece / memory picture (running example).
- Few lines to type per message; never rushed table-only glosses.
- See `.cursor/rules/agentforge-teaching-style.mdc` and [../BUILD_GUIDE.md](../BUILD_GUIDE.md).

## Setup docs

- [SETUP_AZURE.md](./SETUP_AZURE.md)
- [SETUP_PINECONE.md](./SETUP_PINECONE.md)
- [VERIFY_AZURE_PINECONE.md](./VERIFY_AZURE_PINECONE.md)

## Sections

| # | Section | Done when |
|---|---------|-----------|
| 0–5 | Story through upsert | `Upserted 9 vectors` |
| 6 | Smoke query print loop | Terminal shows Query + ranked ids |
| — | **Next phase** | [PHASE_2B.md](./PHASE_2B.md) hybrid merge |

## Run (in project `scripts/` folder)

```bash
python 03_pinecone_upsert.py
```

Do not paste Python lines into Git Bash — only run the script file.
