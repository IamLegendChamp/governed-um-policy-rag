# Setup: Azure AI Foundry / Azure OpenAI (P01)

Use this the first time Azure appears in the track. Fill values into  
`project_track/governed-um-policy-rag/.env` (never commit `.env`).

**What Azure does here:** turns each policy chunk’s text into a list of numbers (**embedding**). Later it will also write the grounded answer (chat).

---

## A. Create / open a resource

1. Open [Azure Portal](https://portal.azure.com/) and sign in.
2. Search for **Azure OpenAI** or **Azure AI Foundry** / **AI hub**.
3. Create a resource if you do not have one (any region you are allowed to use).
4. Wait until the resource shows **Succeeded**.

---

## B. Deploy an embedding model

1. Open your Azure OpenAI / Foundry resource.
2. Go to **Deployments** (or Foundry **Models + endpoints**).
3. **Create deployment**:
   - Model: something like `text-embedding-3-small` (or `text-embedding-ada-002` if that is all you have).
   - Deployment name: pick a short name, e.g. `text-embedding-3-small`.
4. Copy the **deployment name** exactly — it goes in `.env` as `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`.

Chat / judge deployments (`gpt-4o-mini`, etc.) can wait until phase 3–6.

---

## C. Get endpoint and key

1. In the resource, open **Keys and Endpoint** (or Foundry endpoint blade).
2. Copy:
   - **Endpoint** — looks like `https://YOUR-NAME.openai.azure.com/`
   - **KEY 1** (or Key 2) — long secret string

---

## D. Put values in `.env`

Path: `project_track/governed-um-policy-rag/.env`

```text
AZURE_OPENAI_ENDPOINT=https://YOUR-NAME.openai.azure.com/
AZURE_OPENAI_API_KEY=paste-key-here
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

Rules:

- No quotes unless your tooling requires them.
- Endpoint usually ends with `/`.
- Deployment name must match the portal **exactly** (case-sensitive).

---

## E. Sanity check (later, after packages installed)

When `openai` is installed and `.env` is filled, a tiny script or REPL call that embeds `"What is step therapy?"` should return a list of floats (often length 1536 for `text-embedding-3-small`). If you get 401/404, fix key, endpoint, or deployment name — not the RAG logic.

---

## Common failures

| Symptom | Likely cause |
|---------|----------------|
| 401 Unauthorized | Wrong or rotated API key |
| 404 DeploymentNotFound | Deployment name typo or not created |
| Connection / DNS | Typo in endpoint hostname |
| Region / quota | Embedding model not approved for your subscription |

Never paste real keys into chat, commits, or screenshots.
