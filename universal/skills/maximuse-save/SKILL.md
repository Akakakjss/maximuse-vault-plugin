---
name: maximuse-save
description: Checkpoint this chat to the Maximuse Vault. `$maximuse-save [name]` writes a step note, rebuilds the handoff with that name (the one `$maximuse-setup <name>` started) from the notes and freshly checked state, and prints the command to resume it in a new chat. Use when the user asks to save, checkpoint or update a handoff, says "maximuse save", or before starting a fresh chat on long work.
---

# Save to the Maximuse Vault

Vault: `{{VAULT}}`. Note rules: the "Maximuse Vault" section of AGENTS.md.

Requested name: the text the user typed after the command (may be empty).

First run the finder with the workspace folder, adding `--name <text>` when a name was given:

```
"{{PYTHON}}" "{{HOME}}/scripts/vault_find.py" --vault "{{VAULT}}" "<workspace folder>" --name <text>
```

It prints the resolved `VAULT:` (use that path for every note), `TEMPLATES:` (copy note templates from there), the handoffs matching the name (an exact name first, marked `exact: yes`), and any handoff matching this folder. If it prints `VAULT MISSING`, run `$maximuse-setup` first.

1. **Pick the handoff to update.** Never rename a handoff's folder.
   - **A name was given:** a match marked `exact: yes` is the handoff. With no exact match, one partial match is the handoff (say which); several: list them and ask. No match: create it under exactly that name:
     ```
     "{{PYTHON}}" "{{HOME}}/scripts/vault_setup.py" --vault "{{VAULT}}" --handoff "<name>" --cwd "<workspace folder>"
     ```
     (add `--project General` if this chat has no project folder).
   - **No name:** the handoff this chat already set up, resumed or saved; otherwise the MATCH for this folder if it describes this chat's work; otherwise create one with the script above, named `<YYYY-MM-DD> <short topic>`.
2. **Step note.** Write one for the work since the last step note (200 words at most).
3. **Rebuild `00 Handoff.md` from the template.** Check the real state now (git status/log, tests/build) and build the handoff from the step notes and that checked state, never by summarizing the old handoff. Set `cwd:` to the exact workspace folder, `status:` to in-progress, blocked or done, and `updated:`. Copy key values word for word, and fill in "Don't retry" and "Your preferences from this chat". Append new decisions to Decisions.md and new traps to Gotchas.md. Keep the handoff under about 6,000 characters.
4. **Self-check.** Re-read the handoff and ask: could a fresh agent continue from this alone, without this chat? Fix any gaps.
5. **Tell the user the name and how to continue.** Say: "Handoff saved as **<Project> / <session folder>**. To continue, start a new chat in this folder (Codex CLI: `/new`) and type `$maximuse-resume <session folder>`." This tool can't clear the chat by itself, so don't try. If status is done, say the work is finished instead.
