---
name: setup
description: Start this chat's handoff and get to work, or create the Maximuse Vault. `/maximuse:setup <what you want done>` names the handoff from the task, renames the desktop chat to the same name (so `/maximuse:resume <chat name>` finds it later), then starts the task; `/maximuse:setup "<name>" <task>` uses your own name; `/maximuse:setup <folder>` creates or adopts the vault and checks the plugin's Python command and hook. Use on first run, at the start of a piece of work, when the hook or finder reports the vault folder is missing, or when the user wants to move the vault.
argument-hint: "<what you want done> | \"<name>\" <task> | <vault folder>"
---

# Start a handoff, or set up the Maximuse Vault

Configured vault: `${user_config.vault_path}`. Configured Python: `${user_config.python}`.

Requested: `$ARGUMENTS`

1. **Read the request.**
   - Text that is only a folder path (it has `\` or `/`, or starts with `~`) is a **vault folder**: do step 2 and stop after step 5.
   - Text that starts with a quoted part (`"checkout redesign" add discounts`) gives the **name** in the quotes, exactly as typed; the rest is the **task**.
   - Any other text is the **task**. Make the name from it: 2 to 5 plain words saying what the work is (e.g. "Cart discount codes"), the way a chat title reads. No date.
   - Nothing at all: set up or check the configured vault, then ask what the user wants to work on.
2. **Vault folder.** Use the requested folder if one was given, otherwise the configured vault. If the user gave a folder that differs from the configured one, say that the plugin option must point at it too, and tell them how: run `/plugin configure maximuse@maximuse` in Claude Code. The option takes effect in the next session. Until then, pass the new folder to the scripts below with `--vault`.
   If that folder doesn't exist yet, or a folder was requested, preview first and show the user what will be added:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_setup.py" --vault "<folder>" --dry-run
   ```

   Then run it again without `--dry-run`. It creates `Home.md`, `_System/Templates/` and `Projects/`, and never overwrites a file that already exists, so adopting a vault the user already uses only fills in what is missing.
   If the Python command fails (not found, or it opens the Microsoft Store), stop and tell the user to set the plugin's "Python 3 command" option to a working Python 3, such as `python` on Windows, `python3` on macOS and Linux, or the full path to `python.exe`.
3. **Create the handoff** with the script, so its folder is exactly the name:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_setup.py" --vault "<folder>" --handoff "<name>" --cwd "<current working directory>" --chat "<name>"
   ```

   Add `--project General` if this chat has no project folder. The script creates `Projects/<Project>/Sessions/<name>/00 Handoff.md` with `cwd:` and `chat:` set, plus the project's Brief, Decisions and Gotchas and its `Home.md` link if the project is new. It drops only the characters Windows forbids in folder names (`< > : " / \ | ? *`).
   - **`HANDOFF EXISTS` for a name you made up:** add a word that tells them apart and run it again.
   - **`HANDOFF EXISTS` for the user's quoted name:** names are unique across the vault, so nothing was created. Say so, and offer `/maximuse:resume <name>` to continue it, or another name.
   - **`HANDOFF CREATED`:** fill in the handoff's "Goal and status" from the task. If the project is new, fill in what you know of its Brief.
4. **Name the chat the same.** In the Claude desktop app, rename this chat to the name with `mcp__ccd_session_mgmt__set_session_title` (`session_id: "self"`); if it's only listed as deferred, load it first with ToolSearch `select:mcp__ccd_session_mgmt__set_session_title`. Then the sidebar shows the handoff's name. If the tool is missing (terminal) or the rename is refused, leave the `chat:` line as it is.
5. **Report in one or two lines:** the handoff's name (**<Project> / <name>**), and that `/maximuse:save` updates it and `/maximuse:resume <name>` continues it in any chat. The first time, mention that Claude asks permission before writing notes outside the project folder, and that the install guide shows how to allow the vault folder once. When step 2 created or adopted the vault, also report what was added or kept, and run the finder to check the hook:

   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "<folder>" "<current working directory>"
   ```

6. **Start the task** the user gave, keeping step notes and the handoff current per the rules.
