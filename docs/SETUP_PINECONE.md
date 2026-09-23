# Setup: Pinecone (P01)

Use this the first time Pinecone appears in the track. Fill values into  
`project_track/governed-um-policy-rag/.env` (never commit `.env`).

**What Pinecone does here:** stores each chunk’s embedding under a stable id (`C0000`, `C0001`, …) so we can ask “which chunks are closest in meaning to this question?”

---

## A. Create an account

1. Open [https://app.pinecone.io/](https://app.pinecone.io/) and sign up / log in.
2. Use the free (Starter) plan for portfolio work unless you already have org access.

---

## B. Create an API key

1. Open **API Keys** (project settings).
2. Create a key (or copy an existing one).
3. Paste into `.env`:

```text
PINECONE_API_KEY=paste-key-here
```

Treat it like a password.

---

## C. Create an index

Embeddings must match the index **dimension**. For `text-embedding-3-small` that is usually **1536**.

1. Open **Indexes** → **Create index**.
2. Suggested settings for P01:
   - **Name:** `governed-um-policy-rag` (must match `PINECONE_INDEX_NAME` in `.env`)
   - **Dimensions:** `1536` (change only if your embedding model uses a different size)
   - **Metric:** `cosine` (good default for text embeddings)
   - Cloud / region: any free-tier option you are offered (e.g. AWS `us-east-1`)
3. Create and wait until the index is **Ready**.

Optional later: if the console shows a **host** URL, you can set:

```text
# PINECONE_HOST=https://your-index-xxxx.svc.pinecone.io
```

Many SDK flows only need API key + index name.

---

## D. Put values in `.env`

```text
PINECONE_API_KEY=paste-key-here
PINECONE_INDEX_NAME=governed-um-policy-rag
```

---

## E. What “upsert” means (naive)

- **Upsert** = insert or update a vector for one chunk.
- We send: id (`C0002`) + vector (list of floats) + metadata (`source`, `doc_type`, …).
- Later search returns the closest ids + scores for `"What is step therapy?"`.

### Correct call shape (common mistake)

`upsert` is **not** a bare function. It is a **method on the index object** you already opened:

```python
index = get_pinecone_index()          # open the shelf
index.upsert(vectors=records)         # put boxes on THAT shelf
```

Wrong (causes `NameError: name 'upsert' is not defined`):

```python
index = upsert(vectors=records)       # Python looks for a function named upsert — there isn't one
```

Proof in portals: [VERIFY_AZURE_PINECONE.md](./VERIFY_AZURE_PINECONE.md)

---

## Common failures

| Symptom | Likely cause |
|---------|----------------|
| 401 / unauthorized | Bad API key |
| Index not found | Name mismatch vs `.env` |
| Dimension mismatch | Index dim ≠ embedding length (e.g. 1536 vs 3072) |
| Empty query results | Nothing upserted yet, or wrong index |

Never paste real keys into chat, commits, or screenshots.
