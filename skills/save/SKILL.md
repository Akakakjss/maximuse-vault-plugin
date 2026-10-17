---
name: save
description: Checkpoint to the Maximuse Vault, then clear the chat. `/maximuse:save [name]` writes a step note, rebuilds this conversation's named handoff from the notes and freshly checked state, prints the resume command, then clears so the chat reloads from the handoff. Use when the user asks to save, checkpoint or update a handoff, or before clearing a long chat.
argument-hint: "[name]"
---

# Save to the Maximuse Vault, then clear

Vault: `${user_config.vault_path}`. Note layout and rules come from the plugin's SessionStart hook ("Maximuse Vault: session notes and handoffs"); the full text is in `${CLAUDE_PLUGIN_ROOT}/rules/vault-rules.md`.

Requested name: `$ARGUMENTS`

First run the finder with the current working directory, adding `--name <text>` when a name was given:

```
"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "${user_config.vault_path}" "<current working directory>" --name <text>
```

It prints the resolved `VAULT:` (use that path for every note), `TEMPLATES:` (the folder to copy note templates from), and any handoff already matching this folder. If it prints `VAULT MISSING`, tell the user to run `/maximuse:setup` and stop.

**Handoff names.** Every handoff is named by its session folder, shown as `<Project> / <YYYY-MM-DD> <topic>`. Each conversation has its own, so parallel chats never share one.

1. **Session folder (this sets the handoff's name).** If this conversation has no session folder yet, create `Projects/<Project>/Sessions/<YYYY-MM-DD> <topic>/`. Use the name the user gave as `<topic>`, otherwise a short descriptive one, and make it unique within the project. `<Project>` is the working folder's name, or `General` for chats without a project folder. If the folder already exists and the user gave a new name, rename the folder; links between its notes still work. If the project is new, create its Brief, Decisions and Gotchas from the templates and link the Brief under "Projects" in `Home.md`.
2. **Step note.** Write one for the work since the last step note (200 words at most).
3. **Rebuild `00 Handoff.md` from the template.** Check the real state now (git status/log, tests/build) and build the handoff from the step notes and that checked state, never by summarizing the old handoff. Set `cwd:` to the exact current working directory, `status:` to in-progress, blocked or done, and `updated:`. Copy key values word for word, and fill in "Don't retry" and "Your preferences from this chat". Append new decisions to Decisions.md and new traps to Gotchas.md. Keep the handoff under about 6,000 characters: the hook reloads at most about 9,500 characters in all, and the Brief and rules share that room.
4. **Self-check.** Re-read the handoff and ask: could a fresh agent continue from this alone, without this conversation? Fix any gaps.
5. **Tell the user the name.** Before clearing, always say: "Handoff saved as **<Project> / <session folder>**. To continue in a new chat: `/maximuse:resume <session folder topic>`."
6. **Clear the chat.** Unless status is done, first mark this folder for a full reload. The desktop app's clear restarts the session as a plain startup, so without the mark the hook only points to the handoff:
   ```
   "${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "${user_config.vault_path}" "<current working directory>" --mark-reload
   ```
   - **Claude desktop app:** say in one line that the chat will now clear and reload the handoff. Then call `mcp__ccd_session_mgmt__clear_session` with `session_id: "self"`; if the tool is only listed as deferred, load it first with ToolSearch `select:mcp__ccd_session_mgmt__clear_session`. The clear happens when this turn ends and needs the user's approval. The SessionStart hook then injects the Brief and Handoff, and the user's next message resumes from them.
   - **Terminal, or the tool is unavailable or refused:** tell the user to type `/clear` (not `/compact`); the hook will reload the handoff.
   - **Status is done:** say the work is finished. Nothing is reloaded after the clear.
