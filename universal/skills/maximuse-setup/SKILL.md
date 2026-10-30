---
name: maximuse-setup
description: Start this chat's Maximuse handoff and get to work, or create the Maximuse Vault. `$maximuse-setup <what you want done>` names the handoff from the task, then starts the task; `$maximuse-setup "<name>" <task>` uses your own name. Use when the user starts a piece of work with it, says "maximuse setup", or the finder reports the vault is missing.
---

# Start a handoff, or set up the Maximuse Vault

Vault: `{{VAULT}}`. Python: `{{PYTHON}}`. Note rules: the "Maximuse Vault" section of AGENTS.md.

Requested: the text the user typed after the command (may be empty).

1. **Read the request.**
   - Text that starts with a quoted part (`"checkout redesign" add discounts`) gives the **name** in the quotes, exactly as typed; the rest is the **task**.
   - Any other text is the **task**. Make the name from it: 2 to 5 plain words saying what the work is (e.g. "Cart discount codes"), the way a chat title reads. No date.
   - Nothing at all: create or check the vault, show what it added or kept, ask what the user wants to work on, and stop:
     ```
     "{{PYTHON}}" "{{HOME}}/scripts/vault_setup.py" --vault "{{VAULT}}"
     ```
2. **Create the handoff** with the script, so its folder is exactly the name:
   ```
   "{{PYTHON}}" "{{HOME}}/scripts/vault_setup.py" --vault "{{VAULT}}" --handoff "<name>" --cwd "<workspace folder>" --chat "<name>"
   ```
   Add `--project General` if this chat has no project folder. The script creates `Projects/<Project>/Sessions/<name>/00 Handoff.md` with `cwd:` and `chat:` set, plus the project's Brief, Decisions and Gotchas and its `Home.md` link if the project is new. It drops only the characters Windows forbids in folder names.
   - **`HANDOFF EXISTS` for a name you made up:** add a word that tells them apart and run it again.
   - **`HANDOFF EXISTS` for the user's quoted name:** names are unique across the vault, so nothing was created. Say so, and offer `$maximuse-resume <name>` to continue it, or another name.
   - **`HANDOFF CREATED`:** fill in the handoff's "Goal and status" from the task. If the project is new, fill in what you know of its Brief.
3. **Report in one line:** the handoff's name (**<Project> / <name>**), and that `$maximuse-save` updates it and `$maximuse-resume <name>` continues it in a new chat. If writing to the vault was blocked by the sandbox, tell the user to add the vault to `writable_roots` (see the Maximuse universal README) and stop.
4. **Start the task** the user gave, keeping step notes and the handoff current per the AGENTS.md rules.
