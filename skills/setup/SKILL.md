---
name: setup
description: Start a named handoff, and create or adopt the Maximuse Vault folder. `/maximuse:setup <name>` creates this chat's handoff under exactly that name, so `/maximuse:save <name>` updates it later; `/maximuse:setup <folder>` creates or adopts the vault and checks that the plugin's Python command and hook work. Use on first run, when the user names a new piece of work, when the hook or finder reports the vault folder is missing, or when the user wants to move the vault.
argument-hint: "<handoff name> | <vault folder>"
---

# Set up the Maximuse Vault and start a named handoff

Configured vault: `${user_config.vault_path}`. Configured Python: `${user_config.python}`.

Requested: `$ARGUMENTS`

1. **Read the request.** Text that looks like a folder path (it has `\` or `/`, or starts with `~`) is a **vault folder**. Any other text is a **handoff name**: keep it exactly as typed, with no date and no rewording. Nothing at all means: set up or check the configured vault only.
2. **Vault folder.** Use the requested folder if one was given, otherwise the configured vault. If the user gave a folder that differs from the configured one, say that the plugin option must point at it too, and tell them how: run `/plugin configure maximuse@maximuse` in Claude Code. The option takes effect in the next session. Until then, pass the new folder to the scripts below with `--vault`.
   If that folder doesn't exist yet, or a folder was requested, preview first and show the user what will be added:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_setup.py" --vault "<folder>" --dry-run
   ```

   Then run it again without `--dry-run`. It creates `Home.md`, `_System/Templates/` and `Projects/`, and never overwrites a file that already exists, so adopting a vault the user already uses only fills in what is missing.
   If the Python command fails (not found, or it opens the Microsoft Store), stop and tell the user to set the plugin's "Python 3 command" option to a working Python 3, such as `python` on Windows, `python3` on macOS and Linux, or the full path to `python.exe`.
3. **Handoff name.** Create the handoff with the script, so its name is exactly the user's text:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_setup.py" --vault "<folder>" --handoff "<name>" --cwd "<current working directory>"
   ```

   Add `--project General` if this chat has no project folder. The script creates `Projects/<Project>/Sessions/<name>/00 Handoff.md` with `cwd:` set, plus the project's Brief, Decisions and Gotchas and its `Home.md` link if the project is new. It drops only the characters Windows forbids in folder names (`< > : " / \ | ? *`).
   - **`HANDOFF CREATED`:** fill in the handoff's "Goal and status" from what the user said they're working on (leave it as the template if they said nothing). If the project is new, fill in what you know of its Brief.
   - **`HANDOFF EXISTS`:** names are unique across the vault, so nothing was created. Say so, and offer `/maximuse:resume <name>` to continue it or another name to start fresh.
4. **Check the hook.** Run the finder against the folder and report what it prints:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "<folder>" "<current working directory>"
   ```

5. **Report** the vault path, what was added or kept, the handoff's name (**<Project> / <name>**) if one was started, and the commands: `/maximuse:save <name>` (updates that handoff, then clears the chat), `/maximuse:resume <name>` (continues it in any chat), `/maximuse:usage`. Mention that Claude asks permission the first time it writes notes outside the project folder, and that the install guide shows how to allow the vault folder once.
