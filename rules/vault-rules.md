<!--
The SessionStart hook injects everything from the first heading down, every
session, with {{VAULT}} replaced by the vault folder. If you turn the
plugin's "Load the note rules every session" option off, paste this section
into ~/.claude/CLAUDE.md instead and replace {{VAULT}} yourself.
-->
# Maximuse Vault: session notes and handoffs

The user has the Maximuse Vault plugin installed and keeps working notes in an Obsidian vault at `{{VAULT}}` (`[[wikilinks]]`, templates in `_System/Templates/`). These are the user's conventions for it. Notes are for multi-step work (editing files, builds, research), not quick questions.

**Layout.** `Projects/<Project>/` holds `Brief.md` (goal, definition of done, constraints, user preferences; edited deliberately, never summarized), `Decisions.md` (append-only: date · decision · why · rejected options), `Gotchas.md`, and `Sessions/<YYYY-MM-DD> <topic>/` with `00 Handoff.md` plus step notes `01 <step>.md`, `02 …`. `<Project>` is the working folder's name; chats with no project folder use `Projects/General/`. A new project's Brief gets linked under "Projects" in `Home.md`. Notes in other folders are linked by vault path, e.g. `[[Projects/<Project>/Brief|Brief]]`.

**Step notes.** One after a commit, a passing test or build, a decision, or the end of a user request, not after every message. At most ~200 words: what was done, files touched, commit, result, links to the previous/next step and the handoff. The write goes alongside another tool call when possible.

**Handoff (`00 Handoff.md`).** Kept current from the template. `cwd:` is the exact working directory (the resume hook matches on it); `status:` is in-progress, blocked or done. Values are copied word for word (numbers, paths, IDs, commands, error text). It is rebuilt from the step notes and freshly checked state, never by summarizing an older handoff. Before the context passes ~250k tokens, or when the user is stepping away, suggest `/maximuse:save` (writes the notes, then clears and reloads). In the terminal CLI, update the handoff and suggest typing `/clear` (not `/compact`).

**Resuming** (after `/clear`, compaction, or a new chat that continues earlier work): read the Brief and Handoff (the hook adds them when the folder matches; otherwise `/maximuse:resume <name>`), check the real state (git status/log, the test command) before acting, restate the next step, and honor "Don't retry". Notes are claims; code, git and tests are the truth. Where they disagree, trust the code and fix the note. Follow links only to fill a specific gap; if the vault doesn't answer it, ask the user.
