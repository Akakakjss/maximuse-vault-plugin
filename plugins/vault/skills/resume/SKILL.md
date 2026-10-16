---
name: resume
description: Resume earlier work from a Claude Vault handoff by name. `/vault:resume <part of the name>` loads that handoff, the project's Brief, its step notes, Decisions and Gotchas, then checks the real state before continuing. Use when the user asks to resume, continue or pick up earlier work, or names a handoff.
argument-hint: "<part of the handoff name>"
---

# Resume from the Claude Vault

Vault: `${user_config.vault_path}`. Note layout and rules come from the plugin's SessionStart hook ("Claude Vault: session notes and handoffs"); the full text is in `${CLAUDE_PLUGIN_ROOT}/rules/vault-rules.md`.

**Handoff names.** Every handoff is named by its session folder, shown as `<Project> / <YYYY-MM-DD> <topic>`. Each conversation has its own, so parallel chats never share one. The user picks one by typing any unique part of the name, e.g. `/vault:resume vault setup`.

Requested name: `$ARGUMENTS`

First run the finder with the current working directory, adding `--name <text>` when a name was given:

```
"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/vault_find.py" --vault "${user_config.vault_path}" "<current working directory>" --name <text>
```

It prints the resolved `VAULT:` (use that path for every note), the handoffs matching the name, the handoff matching this folder, and recent unfinished handoffs, each with its note paths. If it prints `VAULT MISSING`, tell the user to run `/vault:setup` and stop.

1. **Choose the handoff by name.**
   - **No name given:** don't pick one yourself, even if a handoff matches this folder. Remind the user: "Tell me which handoff to resume: `/vault:resume <name>`." Then list the RECENT UNFINISHED names (and the MATCH for this folder, if any, marked as such) and stop until they answer.
   - **One match for the name:** use it.
   - **Several matches:** list their names and ask which one.
   - **None:** say so and show the RECENT UNFINISHED names.
2. **Read everything, in this order:** the project's Brief, the Handoff, every step note in its session folder, Decisions, Gotchas. Follow other links only to fill a specific gap.
3. **Re-point it here.** If the handoff's `cwd:` differs from the current working directory, set it to the current one so the resume hook finds it after a clear, and add one line under "Checked state" noting the move.
4. **Check the real state before acting:** git status/log and the test/build command named in "Checked state" or the Brief. Where notes and reality disagree, trust reality and fix the note.
5. **Report briefly:** the goal, the verified state, the "Don't retry" items, and the next step. Continue if the user's message asked you to; otherwise ask whether to start the next step.
6. **Keep notes as you work.** Write step notes and keep the handoff current per the rules. When the task ends, update the handoff for the next agent (`status: done` if finished).
