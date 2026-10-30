---
name: maximuse-resume
description: Resume earlier work from a Maximuse Vault handoff by name. `$maximuse-resume <name or chat title> [what to do next]` loads that handoff, the project's Brief, its step notes, Decisions and Gotchas, then checks the real state before continuing. Use when the user asks to resume, continue or pick up earlier work, says "maximuse resume", or names a handoff.
---

# Resume from the Maximuse Vault

Vault: `{{VAULT}}`. Note rules: the "Maximuse Vault" section of AGENTS.md.

Requested name: the text the user typed after the command. If it is a name followed by a request, the name is its first few words: pass the longest run of first words that finds a match, and treat the rest as the user's task.

First run the finder with the workspace folder, adding `--name <text>` when a name was given:

```
"{{PYTHON}}" "{{HOME}}/scripts/vault_find.py" --vault "{{VAULT}}" "<workspace folder>" --name <text>
```

It prints the resolved `VAULT:`, the handoffs matching the name by folder or chat title, words in any order (an exact match first, marked `exact: yes`), the handoff matching this folder, and recent unfinished handoffs, each with its note paths. If it prints `VAULT MISSING`, run `$maximuse-setup` first.

1. **Choose the handoff by name.**
   - **No name given:** don't pick one yourself. List the RECENT UNFINISHED handoffs with their numbers (and the MATCH for this folder, marked as such), say "Tell me which one: its number or name", and stop.
   - **A number:** the handoff with that number in the RECENT UNFINISHED list.
   - **An exact match, or one match:** use it. **Several:** list their names and ask. **None:** say so and show the RECENT UNFINISHED names.
2. **Read everything, in this order:** the project's Brief, the Handoff, every step note in its session folder, Decisions, Gotchas. Follow other links only to fill a specific gap.
3. **Re-point it here.** If the handoff's `cwd:` differs from the workspace folder, set it to this one and add one line under "Checked state" noting the move.
4. **Check the real state before acting:** git status/log and the test/build command named in "Checked state" or the Brief. Where notes and reality disagree, trust reality and fix the note.
5. **Report briefly:** the goal, the verified state, the "Don't retry" items, and the next step. Continue if the user asked you to; otherwise ask whether to start the next step.
6. **Keep notes as you work**, per the AGENTS.md rules. Save with `$maximuse-save`.
