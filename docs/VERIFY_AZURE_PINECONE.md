# Verify: proof in Azure + Pinecone (P01 phase 2a)

You already proved a lot in the **terminal**. The portals show the same work from the vendor side.

Never screenshot API keys. Never paste keys into chat.

---

## A. Proof in the terminal (fastest)

From `scripts/`:

```bash
python 03_pinecone_upsert.py
```

| Line you see | What it proves |
|--------------|----------------|
| `Loaded 9 chunks...` | Local catalog read |
| `Sample embed ok: ... dim=1536` | **Azure** embedding API accepted your key/endpoint/deployment |
| `Pinecone index open: governed-um-policy-rag` | **Pinecone** accepted your API key + index name |
| `Upserted 9 vectors -> Pinecone` | Vectors were written (after the upsert line is fixed) |

If embed works but upsert fails, Azure is fine and the bug is only the Pinecone write call.

---

## B. Proof in Azure Portal / Foundry

1. Open [Azure Portal](https://portal.azure.com/) → your **Azure OpenAI** / **AI Foundry** resource.
2. Open **Deployments** (or Foundry **Models + endpoints**).
3. Confirm your embedding deployment name matches `.env` `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`.
4. Open **Metrics** (or Monitoring) for that resource / deployment:
   - Look for **Tokens** / **Calls** / **Requests** around the time you ran the script.
   - A spike when you ran `03_pinecone_upsert.py` = Azure really received embed calls.

Optional: Azure OpenAI Studio / Foundry **Playground → Embeddings** — paste a short sentence and generate; that is the same family of API your script calls.

Azure does **not** show your Pinecone vectors. It only shows that embeddings were requested.

---

## C. Proof in Pinecone console

1. Open [https://app.pinecone.io/](https://app.pinecone.io/).
2. Click index **`governed-um-policy-rag`**.
3. Check **Overview**:
   - **Vector count** should move toward **9** after a successful upsert (refresh if needed; small delay is normal).
   - **Dimension** should be **1536**.
4. Open **Browser** / **Query** / **Records** (label varies by UI version):
   - Look for ids `C0000`, `C0001`, … `C0008`.
   - Open one record: you should see **metadata** (`source`, `doc_type`, `classification`) and a long **values** vector (or truncated preview).
5. Optional **Query** tab: you need a 1536-float query vector (your next script section will do this). The console alone cannot turn English into a vector without an embedding call.

If vector count stays **0**, upsert never succeeded (fix the script error first).

---

## D. What each system owns

```text
chunks.jsonl     ->  you (disk)
Azure embed API  ->  text to 1536 floats
Pinecone index   ->  stores floats + id + metadata
```

---

## E. After upsert works

Next coaching step: smoke **query** in Python (embed `"What is step therapy?"` → `index.query` → print top `C00xx`). That is the clearest end-to-end proof.
