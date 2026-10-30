---
name: save
description: Checkpoint to the Maximuse Vault, then clear the chat. `/maximuse:save` (or `/maximuse:save <name>`) writes a step note, rebuilds this chat's handoff (the one `/maximuse:setup` started) from the notes and freshly checked state, prints the resume command, then clears so the chat reloads from the handoff. Use when the user asks to save, checkpoint or update a handoff, or before clearing a long chat.
argument-hint: "[name or chat title]"
---

# Save to the Maximuse Vault, then clear

Vault: `${user_config.vault_path}`. Note layout and rules come from the plugin's SessionStart hook ("Maximuse Vault: session notes and handoffs"); the full text is in `${CLAUDE_PLUGIN_ROOT}/rules/vault-rules.md`.

Requested name: `$ARGUMENTS`

First run the finder with the current working directory, adding `--name <text>` when a name was given:

```
"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "${user_config.vault_path}" "<current working directory>" --name <text>
```

It prints the resolved `VAULT:` (use that path for every note), `TEMPLATES:` (the folder to copy note templates from), the handoffs matching the name by folder or chat title (an exact match is listed first and marked `exact: yes`), and any handoff already matching this folder. If it prints `VAULT MISSING`, tell the user to run `/maximuse:setup` and stop.

**Handoff names.** A handoff is named by its session folder, shown as `<Project> / <session folder>`, and its `chat:` line holds the chat's title. `/maximuse:setup` names it (from the task, or the user's quoted name) and, in the desktop app, gives the chat the same title. Each conversation has its own, so parallel chats never share one. Never rename a handoff's folder.

1. **Pick the handoff to update.**
   - **No name (the usual case):** the handoff this conversation already set up, resumed or saved. Otherwise the MATCH for this folder if it describes this conversation's work. Otherwise create one as `/maximuse:setup` would: a 2–5 word name from this chat's work (in the desktop app, the chat's title if it describes the work), with the script below, then rename the chat to it with `mcp__ccd_session_mgmt__set_session_title` (`session_id: "self"`) where that tool exists.
   - **A name was given** (a folder name or a chat title): a match marked `exact: yes` is the handoff; update it. With no exact match, one other match is the handoff (say which one you're updating); several: list them and ask. No match: create it under exactly that name:
     ```
     "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_setup.py" --vault "${user_config.vault_path}" --handoff "<name>" --cwd "<current working directory>" --chat "<name>"
     ```
     (add `--project General` if this chat has no project folder).
   - If the project is new, fill in what you know of its Brief.
2. **Step note.** Write one for the work since the last step note (200 words at most).
3. **Rebuild `00 Handoff.md` from the template.** Check the real state now (git status/log, tests/build) and build the handoff from the step notes and that checked state, never by summarizing the old handoff. Set `cwd:` to the exact current working directory, `chat:` to this chat's current title (desktop app: `mcp__ccd_session_mgmt__get_session` with `session_id: "self"`, so a chat the user renamed is still found by its new title; elsewhere keep the line as it is), `status:` to in-progress, blocked or done, and `updated:`. Copy key values word for word, and fill in "Don't retry" and "Your preferences from this chat". Append new decisions to Decisions.md and new traps to Gotchas.md. Keep the handoff under about 6,000 characters: the hook reloads at most about 9,500 characters in all, and the Brief and rules share that room.
4. **Self-check.** Re-read the handoff and ask: could a fresh agent continue from this alone, without this conversation? Fix any gaps.
5. **Tell the user the name.** Before clearing, always say: "Handoff saved as **<Project> / <session folder>**. To continue in a new chat: `/maximuse:resume <session folder>`."
6. **Clear the chat.** Unless status is done, first mark this folder for a full reload. The desktop app's clear restarts the session as a plain startup, so without the mark the hook only points to the handoff:
   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "${user_config.vault_path}" "<current working directory>" --mark-reload
   ```
   - **Claude desktop app:** say in one line that the chat will now clear and reload the handoff. Then call `mcp__ccd_session_mgmt__clear_session` with `session_id: "self"`; if the tool is only listed as deferred, load it first with ToolSearch `select:mcp__ccd_session_mgmt__clear_session`. The clear happens when this turn ends and needs the user's approval. The SessionStart hook then injects the Brief and Handoff, and the user's next message resumes from them.
   - **Terminal, or the tool is unavailable or refused:** tell the user to type `/clear` (not `/compact`); the hook will reload the handoff.
   - **Status is done:** say the work is finished. Nothing is reloaded after the clear.
