# Publishing hygiene

A public repository is a publication. The moment you push, the diff is permanent in someone's
history and searchable. Scan before you push, and check the artefact afterwards — not your local
working tree.

## 1. What must never be committed

- **build artefacts**: `__pycache__/`, `*.pyc`, `node_modules/`, `.venv/`, `dist/`, `build/`,
  `.DS_Store`, editor swap files;
- **secrets**: private keys, tokens, `.env` files, credentials in examples;
- **personal data**: real names, emails, home directory paths containing a username, private or
  public IP addresses, account identifiers;
- **local state**: databases, logs, caches, screenshots of a live system.

A scratch directory used to build the commit is exactly where these accumulate. Delete or ignore
them before staging; if they reach the index, remove them from the index in the same pull request
and add an ignore rule, so the next person cannot repeat it.

## 2. Scan, then look

Run the scrub (`scripts/repo_scrub.py`) for the mechanical checks. Then read **the file list** the
way a stranger would:

- does every file belong to the topic?
- is anything binary, generated, or much larger than its purpose?
- would a reader learn anything about a real person, company or machine from these files?

## 3. Rewrite examples, never redact them

`user@example.com` teaches the same lesson as a real address and carries no information. A pattern
that has to be blanked out is a pattern you can replace outright with an invented one.

## 4. After the push

Check the pull request's file list, not `git status`. Push state, index state and working-tree state
are three different things, and only the first is what the world sees.
