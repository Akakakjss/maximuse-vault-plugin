---
name: setup
description: Create the Claude Vault folder, or adopt an existing folder as the vault, and check that the plugin's Python command and hook work. Use on first run, when the hook or finder reports the vault folder is missing, or when the user wants to move the vault.
argument-hint: "[folder to create or adopt]"
---

# Set up the Claude Vault

Configured vault: `${user_config.vault_path}`. Configured Python: `${user_config.python}`.

Requested folder: `$ARGUMENTS`

1. **Pick the folder.** Use the requested folder if one was given, otherwise the configured vault. If the user gave a folder that differs from the configured one, say that the plugin option must point at it too, and tell them how: run `/plugin configure vault@maximuse` in Claude Code. The option takes effect in the next session. Until then, pass the new folder to the scripts below with `--vault`.
2. **Preview, then write.** Run the setup script with `--dry-run` first and show the user what it will add:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_setup.py" --vault "<folder>" --dry-run
   ```

   Then run it again without `--dry-run`. It creates `Home.md`, `_System/Templates/` and `Projects/`, and never overwrites a file that already exists, so adopting a vault the user already uses only fills in what is missing.
   If the Python command fails (not found, or it opens the Microsoft Store), stop and tell the user to set the plugin's "Python 3 command" option to a working Python 3, such as `python` on Windows, `python3` on macOS and Linux, or the full path to `python.exe`.
3. **Check the hook.** Run the finder against the folder and report what it prints:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "<folder>" "<current working directory>"
   ```

4. **Report** the vault path, what was added or kept, and the three commands: `/vault:save [name]`, `/vault:resume <name>`, `/vault:usage`. Mention that Claude asks permission the first time it writes notes outside the project folder, and that the install guide shows how to allow the vault folder once.
