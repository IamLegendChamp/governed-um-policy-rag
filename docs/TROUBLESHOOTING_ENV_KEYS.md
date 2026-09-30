# Troubleshooting: "Incorrect API key provided" despite a correct project `.env`

## Symptom

`openai.AuthenticationError: Error code: 401 - Incorrect API key provided: replace-************-key`

The project `.env` has the real key, but the placeholder is what gets sent.
Restarting Cursor, and even opening a brand-new terminal, does **not** fix it.

## Root cause

Two things combine:

1. **A second `.env` exists at the workspace root** (`AgentForge/.env`) containing a
   placeholder `OPENAI_API_KEY=replace-me-with-your-key`. The editor loads the
   workspace-root `.env` into every terminal it opens, so the placeholder is already in
   `os.environ` before Python starts.
2. **`python-dotenv`'s `load_dotenv()` does not override existing environment
   variables by default.** The project `.env` (with the real key) is read, but the
   already-present placeholder wins.

`unset OPENAI_API_KEY` only helps the one terminal it is typed in; the next new terminal
gets the placeholder again (this is why the earlier "fix" stopped working after a few hours).

## How to confirm

In the failing terminal (prints a length only, not the secret):

```bash
echo "shell OPENAI_API_KEY length: ${#OPENAI_API_KEY}"
```

A short length (e.g. `24`) means a placeholder was injected before Python started.
Then look for the source: `find . -maxdepth 3 -name ".env*"` and check the workspace root.

## Permanent fix

In `scripts/03_pinecone_upsert.py`, make the project `.env` authoritative:

```python
load_dotenv(PROJECT_DIR / ".env", override=True)
```

`04_hybrid_search.py` imports `03_pinecone_upsert`, so this covers both scripts.

## Prevention

- Keep placeholder-only values out of any `.env` that the editor auto-loads into
  terminals (comment them out in the workspace-root `.env`).
- For each project, load its own `.env` with `override=True` so project config wins.
- Never `export` secrets manually in a shell for quick tests.
