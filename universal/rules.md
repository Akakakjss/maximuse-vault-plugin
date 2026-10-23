<!--
install.py writes everything from the first heading down into AGENTS.md,
between maximuse:start and maximuse:end markers, with {{VAULT}} and {{HOME}}
filled in. Reinstalling replaces that block; the rest of AGENTS.md is kept.
-->
# Maximuse Vault: session notes and handoffs

The user keeps working notes in an Obsidian vault at `{{VAULT}}` (plain Markdown, `[[wikilinks]]`, templates in `_System/Templates/`), shared with their other AI tools. These are the user's conventions for it. Notes are for multi-step work (editing files, builds, research), not quick questions.

**Commands.** `setup <name>` starts a handoff named exactly `<name>`; `save <name>` updates that handoff; `resume <name>` continues one in a new chat. In Codex they are the skills `$maximuse-setup`, `$maximuse-save`, `$maximuse-resume`; in other tools the user types e.g. `maximuse save <name>`. Either way, follow `{{HOME}}/skills/maximuse-<command>/SKILL.md`.

**Layout.** `Projects/<Project>/` holds `Brief.md` (goal, definition of done, constraints, user preferences; edited deliberately, never summarized), `Decisions.md` (append-only: date · decision · why · rejected options), `Gotchas.md`, and `Sessions/<name>/` with `00 Handoff.md` plus step notes `01 <step>.md`, `02 …`. `<name>` is exactly what the user gave setup or save (`<YYYY-MM-DD> <topic>` only when they gave none); a handoff's folder is never renamed. `<Project>` is the workspace folder's name; chats with no project folder use `Projects/General/`. Notes in other folders are linked by vault path, e.g. `[[Projects/<Project>/Brief|Brief]]`.

**Step notes.** One after a commit, a passing test or build, a decision, or the end of a user request, not after every message. At most ~200 words: what was done, files touched, commit, result, links to the previous/next step and the handoff.

**Handoff (`00 Handoff.md`).** Kept current from the template. `cwd:` is the exact workspace folder; `status:` is in-progress, blocked or done. Values are copied word for word (numbers, paths, IDs, commands, error text). It is rebuilt from the step notes and freshly checked state, never by summarizing an older handoff. When the chat gets long, or the user is stepping away, suggest save; this tool can't clear and reload a chat, so after saving the user starts a new chat and runs resume.

**Resuming:** read the Brief and Handoff, check the real state (git status/log, the test command) before acting, restate the next step, and honor "Don't retry". Notes are claims; code, git and tests are the truth. Where they disagree, trust the code and fix the note. If the vault doesn't answer a question, ask the user.
