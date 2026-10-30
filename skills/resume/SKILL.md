---
name: resume
description: Resume earlier work from a Maximuse Vault handoff by name. `/maximuse:resume <chat title or part of the name> [what to do next]` loads that handoff, the project's Brief, its step notes, Decisions and Gotchas, then checks the real state before continuing. Use when the user asks to resume, continue or pick up earlier work, or names a handoff or an earlier chat.
argument-hint: "<chat title, name or number> [what to do next]"
---

# Resume from the Maximuse Vault

Vault: `${user_config.vault_path}`. Note layout and rules come from the plugin's SessionStart hook ("Maximuse Vault: session notes and handoffs"); the full text is in `${CLAUDE_PLUGIN_ROOT}/rules/vault-rules.md`.

**Handoff names.** Every handoff is named by its session folder, shown as `<Project> / <session folder>`, and its `chat:` line holds the title of the chat it came from; in the desktop app `/maximuse:setup` gives the chat the handoff's name. The user can type the chat's title as it appears in the sidebar, any unique part of the name, its words in any order, or a number from the list, e.g. `/maximuse:resume cart discount`.

If the text after the command is a name followed by a request (e.g. `/maximuse:resume login fix can you add tests`), the name is its first few words: pass the longest run of first words that finds a match, and treat the rest as the user's task.

Requested name: `$ARGUMENTS`

First run the finder with the current working directory, adding `--name <text>` when a name was given:

```
"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "${user_config.vault_path}" "<current working directory>" --name <text>
```

It prints the resolved `VAULT:` (use that path for every note), the handoffs matching the name, the handoff matching this folder, and recent unfinished handoffs, each with its note paths. If it prints `VAULT MISSING`, tell the user to run `/maximuse:setup` and stop.

1. **Choose the handoff by name.**
   - **No name given:** don't pick one yourself, even if a handoff matches this folder. List the RECENT UNFINISHED handoffs with their numbers and chat titles (and the MATCH for this folder, if any, marked as such), say "Tell me which one: its number, name or chat title", and stop until they answer.
   - **A number:** the handoff with that number in the RECENT UNFINISHED list.
   - **One match for the name:** use it.
   - **Several matches:** list their names and ask which one.
   - **None:** say so and show the RECENT UNFINISHED names.
2. **Read everything, in this order:** the project's Brief, the Handoff, every step note in its session folder, Decisions, Gotchas. Follow other links only to fill a specific gap.
3. **Re-point it here.** If the handoff's `cwd:` differs from the current working directory, set it to the current one so the resume hook finds it after a clear, and add one line under "Checked state" noting the move. In the Claude desktop app, also rename this chat to the handoff's name with `mcp__ccd_session_mgmt__set_session_title` (`session_id: "self"`; load it with ToolSearch if deferred) and set `chat:` to that title, so the sidebar keeps pointing at the same handoff.
4. **Check the real state before acting:** git status/log and the test/build command named in "Checked state" or the Brief. Where notes and reality disagree, trust reality and fix the note.
5. **Report briefly:** the goal, the verified state, the "Don't retry" items, and the next step. Continue if the user's message asked you to; otherwise ask whether to start the next step.
6. **Keep notes as you work.** Write step notes and keep the handoff current per the rules. When the task ends, update the handoff for the next agent (`status: done` if finished).
