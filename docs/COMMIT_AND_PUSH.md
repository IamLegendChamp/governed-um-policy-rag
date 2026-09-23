# When to commit and push (P01)

Calm portfolio practice: ship **finished slices**, not half-typed lessons. Do not commit secrets.

## Right time to commit (this repo)

Commit when a **phase checkpoint** works end-to-end and you would be fine showing the code to a recruiter.

| Checkpoint | Commit? | Why |
|------------|---------|-----|
| Chunk script works (`01`) | Optional small commit | Ingest baseline |
| TF-IDF CLI works (`02`) | Yes | Keyword leg is demoable |
| **Azure embed + Pinecone upsert + smoke query (`03`)** | **Yes (now)** | Dense leg is real; good public milestone |
| Mid-typing `04_hybrid_search.py` | **No** | Wait until hybrid prints a merged ranking |
| Hybrid merge works | Yes | Next milestone |
| Grounded answer + citations | Yes | Bigger story commit |

**Rule of thumb:** if the next file is not created yet (e.g. no `04` yet), and the last script runs cleanly—**commit**. Starting the next phase without committing the last one leaves GitHub behind your laptop.

## Before every commit

1. Confirm `.env` is **not** staged (gitignored). Only `.env.example` is public.  
2. No API keys, tokens, or real member/PHI text in diffs.  
3. Prefer removing commented `print("checking...")` debug before push.  
4. `git status` — scan for surprise files.

## Commit message style (this repo)

Short, factual, portfolio tone—what shipped, not how hard it was:

```text
Add Azure embeddings and Pinecone upsert with smoke query.
```

Avoid: “Finally got Pinecone working!!!” / “Epic RAG!!!”

## When to push

Push after a checkpoint commit you want **visible on GitHub** (same milestones as above).  
You do not need to push every local WIP save.

```bash
git status
git add -A   # then re-check: no .env
git commit -m "..."
git push origin main
```

## Parent monorepo (AgentForge)

`AgentForge/` may not be a git root; **this** project publishes at  
https://github.com/IamLegendChamp/governed-um-policy-rag  

Track-wide deploy notes: [../../GITHUB_DEPLOY.md](../../GITHUB_DEPLOY.md)
