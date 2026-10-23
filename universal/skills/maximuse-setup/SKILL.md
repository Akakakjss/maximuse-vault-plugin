---
name: maximuse-setup
description: Start a named Maximuse handoff, or create the Maximuse Vault. `$maximuse-setup <name>` creates this chat's handoff under exactly that name, so `$maximuse-save <name>` updates it later. Use when the user starts a named piece of work, says "maximuse setup", or the finder reports the vault is missing.
---

# Set up the Maximuse Vault and start a named handoff

Vault: `{{VAULT}}`. Python: `{{PYTHON}}`. Note rules: the "Maximuse Vault" section of AGENTS.md.

Requested: the text the user typed after the command (may be empty). Keep a name exactly as typed, with no date and no rewording.

1. **No name:** create or check the vault, show what it added or kept, then stop:
   ```
   "{{PYTHON}}" "{{HOME}}/scripts/vault_setup.py" --vault "{{VAULT}}"
   ```
2. **A name:** create the handoff with the script, so its name is exactly the user's text:
   ```
   "{{PYTHON}}" "{{HOME}}/scripts/vault_setup.py" --vault "{{VAULT}}" --handoff "<name>" --cwd "<workspace folder>"
   ```
   Add `--project General` if this chat has no project folder. The script creates `Projects/<Project>/Sessions/<name>/00 Handoff.md` with `cwd:` set, plus the project's Brief, Decisions and Gotchas and its `Home.md` link if the project is new. It drops only the characters Windows forbids in folder names.
   - **`HANDOFF CREATED`:** fill in the handoff's "Goal and status" from what the user said they're working on. If the project is new, fill in what you know of its Brief.
   - **`HANDOFF EXISTS`:** names are unique across the vault, so nothing was created. Say so, and offer `$maximuse-resume <name>` to continue it, or another name.
3. **Report** the handoff's name (**<Project> / <name>**) and the commands: `$maximuse-save <name>` (updates it), `$maximuse-resume <name>` (continues it in a new chat). If writing to the vault was blocked by the sandbox, tell the user to add the vault to `writable_roots` (see the Maximuse universal README).
