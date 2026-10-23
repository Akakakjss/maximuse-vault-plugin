# Maximuse for Codex and other AGENTS.md agents

The same vault, notes and named handoffs as the Claude Code plugin, for OpenAI Codex (CLI, IDE extension and app) and any agent that reads `AGENTS.md` and can run a command, such as Cursor, GitHub Copilot's coding agent, Jules or Aider. Your Claude Code chats and these agents can share one vault, so work started in one can be resumed in another.

## Install

Needs Python 3.8 or later. From a copy of this repository:

```
git clone https://github.com/akakakjss/maximuse-vault-plugin.git
python maximuse-vault-plugin/universal/install.py --vault "C:\Users\you\Documents\Maximuse Vault"
```

Use `python3` on macOS and Linux. Add `--dry-run` first to see every file it would write. The installer:

| Writes | For |
|---|---|
| `~/.maximuse/scripts`, `~/.maximuse/templates` | the vault scripts and note templates (a copy, so the cloned repo can be deleted) |
| `~/.agents/skills/maximuse-{setup,save,resume}/SKILL.md` | Codex's user skills: `$maximuse-setup`, `$maximuse-save`, `$maximuse-resume` |
| `~/.maximuse/skills/…` | the same instructions, for agents without a skills folder |
| `~/.codex/AGENTS.md` (or `$CODEX_HOME`) | the always-on note rules, between `maximuse:start` and `maximuse:end` markers; the rest of the file is kept |
| the vault | `Home.md`, `_System/Templates/`, `Projects/`; existing notes are never overwritten |

For tools that only read a project's own `AGENTS.md` (Cursor, Copilot, Jules, Aider…), add `--project <repo folder>` (repeatable). Trade-off: a project's `AGENTS.md` is usually committed, and the block names your vault path, so either keep it out of commits or use it only in personal repos. `--no-codex` skips the global Codex file.

**Let Codex write notes.** Codex's default sandbox only writes inside the workspace, and the vault is outside it. Add the vault to `~/.codex/config.toml` (the installer prints this with your path filled in):

```toml
[sandbox_workspace_write]
writable_roots = ['C:\Users\you\Documents\Maximuse Vault']
```

## Use

| Codex | Other AGENTS.md tools | Does |
|---|---|---|
| `$maximuse-setup <name>` | `maximuse setup <name>` | Starts a handoff named exactly `<name>` for this folder. |
| `$maximuse-save <name>` | `maximuse save <name>` | Writes a step note and rebuilds that handoff from checked state. |
| `$maximuse-resume <name>` | `maximuse resume <name>` | In a new chat: loads the handoff, Brief and notes, checks git and tests, reports the next step. |

**What's different from Claude Code.** These agents have no session hook, so `save` can't clear and reload the chat for you. After saving, start a new chat (Codex CLI: `/new`) and run resume with the name. `/maximuse:usage` is Claude Code only, since it reads Claude Code's own transcripts.

## Update and uninstall

Pull the repository and run the same install command again: it replaces only what it wrote. To remove everything (the vault and the rest of each `AGENTS.md` are kept):

```
python maximuse-vault-plugin/universal/install.py --uninstall
```

Add the same `--project` folders you installed into.
