# Troubleshooting: "Incorrect API key provided" despite a correct `.env`

## Symptom

`openai.AuthenticationError: Error code: 401 - Incorrect API key provided: replace-************-key`

...even though `.env` has been checked, confirmed correct, and re-saved multiple times.
Restarting the Cursor/IDE window does **not** fix it.

## Root cause

`python-dotenv`'s `load_dotenv()` **does not override variables that already exist
in the process environment** (`os.environ`) unless called with `override=True`.

If a shell session ever ran `export OPENAI_API_KEY=<placeholder>` (manually, or via
an earlier setup step), that exported value lives for the **entire lifetime of that
shell process** — it is not tied to the `.env` file, not tied to any `.bashrc` /
`.bash_profile` / Windows User or Machine environment variable, and is invisible to
`grep`-ing config files or checking `[Environment]::GetEnvironmentVariable(...)` at
the OS level. Every script run from that same terminal tab will keep using the
stale exported value, silently ignoring whatever the current `.env` file says.

This is **not** a Windows problem and **not** fixed by restarting Cursor — restarting
the editor does not necessarily kill an already-open integrated terminal's shell
process, and even a full IDE restart only helps if it happens to also close that
terminal.

## How to confirm this is the cause

In the *same terminal* that is failing, run (safe — does not print the secret):

```bash
echo "shell-exported OPENAI_API_KEY length: ${#OPENAI_API_KEY}"
```

If this prints a short/unexpected length (e.g. `24`) instead of `0` or the real
key's length, the shell has a stale exported value overriding `.env`.

## The fix

In that terminal:

```bash
unset OPENAI_API_KEY
```

Then re-run the script. `load_dotenv()` will now correctly load the real value from
`.env` since nothing in `os.environ` is blocking it anymore.

Alternatively: open a **brand new terminal tab** — a fresh shell process never picked
up the stale manual export in the first place.

## Prevention

- Never manually `export` real or placeholder secrets into an interactive shell for
  "quick testing" — always go through `.env` + `load_dotenv()`.
- If in doubt after editing `.env`, `unset <VAR>` first, or open a new terminal,
  before re-running.
