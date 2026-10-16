# Maximuse Vault for Claude Code

A Claude Code plugin that keeps step notes and handoffs in an Obsidian vault, so you can clear a long chat at 200–300k tokens and pick it back up in a fresh one without losing the thread. This repository is also a plugin marketplace (`maximuse`), so it installs with two commands.

## Why

Every tool call re-sends the whole conversation. Most of that is billed as cache reads, and cache reads still count against your usage limit. One heavy Pro user's logs showed **98% of all tokens were cache reads**, because chats averaged about **500k tokens of context** (p90 815k) before auto-compact kicked in near the top of a 1M window.

Clearing at ~250k and resuming from a short, accurate handoff keeps the average context per call far lower. The estimate for that user was **about 2× more work from the same limit (1.7–2.1×)**. The catch is handoff quality: a vague handoff costs more in re-reading and mistakes than it saves. The plugin's rules and templates exist to make handoffs good enough to resume from cold: values copied word for word, a "Don't retry" section, and a rule to check the real state before acting.

## What you get

| Piece | What it does |
|---|---|
| `/vault:save [name]` | Writes a step note, rebuilds this chat's handoff from the notes and freshly checked state, prints the resume command, then clears the chat. The hook reloads the handoff into the cleared chat. |
| `/vault:resume <name>` | In any chat, loads a handoff by any unique part of its name, reads the Brief, step notes, Decisions and Gotchas, checks git and tests, and reports the next step. |
| `/vault:setup [folder]` | First run: creates the vault, or adopts a folder you already use without overwriting anything. |
| `/vault:usage` | Compares your token usage (cache-read share, context per call) with a saved baseline. |
| SessionStart hook | Every session it adds the short note rules (~550 tokens). After `/clear`, compaction, or the first start after `/vault:save` it also adds the Brief and the handoff whose `cwd:` matches the folder. On a normal start it only points to an unfinished handoff. |
| Vault templates | `Home.md`, plus Brief, Decisions, Gotchas, Handoff and Step templates under `_System/Templates/`. |

Vault layout:

```
Maximuse Vault/
  Home.md
  _System/Templates/        Brief, Decisions, Gotchas, Handoff, Step
  Projects/<Project>/
    Brief.md  Decisions.md  Gotchas.md
    Sessions/<YYYY-MM-DD> <topic>/
      00 Handoff.md
      01 <step>.md  02 <step>.md ...
```

Each chat has its own session folder, so parallel chats never share a handoff. A handoff's name is `<Project> / <session folder>`.

## Install

See **[INSTALL.md](INSTALL.md)** for install, first run, permissions, troubleshooting and uninstall. Short version:

```
/plugin marketplace add akakakjss/maximuse-vault-plugin
/plugin install vault@maximuse
/vault:setup
```

Requires Python 3.8 or later and a recent Claude Code (tested with v2.1.292 on Windows and v2.1.301 on Linux).

**Where it works:** Claude Code (terminal, IDE extensions and the desktop app's Code tab). The hook and the Python scripts need Claude Code on your own computer; claude.ai chat skips hooks and can't run the scripts, so the plugin does nothing useful there.

## Design notes

**The always-on rules are injected by the hook, not pasted into CLAUDE.md.** A plugin can't edit your CLAUDE.md, and Claude Code doesn't load a CLAUDE.md shipped inside a plugin. Rules only inside a skill aren't enough either, because a skill loads only when invoked, so step notes during normal work would be skipped. The SessionStart hook adds the same ~550-token rules as `additionalContext` on startup, `/clear` and compaction: the same cost as a CLAUDE.md section, with no manual step, and the vault path filled in from your settings. If you'd rather keep them in CLAUDE.md, turn the "Load the note rules every session" option off and paste `rules/vault-rules.md` there.

**Everything the hook injects stays under 9,500 characters.** Claude Code moves `additionalContext` over 10,000 characters into a file and shows Claude only a 2,000-character preview. The hook gives the handoff priority, gives the Brief what's left, and marks any truncation with the note's full path.

**`/clear`, not `/compact`.** A skill can't trigger `/compact`, and a compaction summary is lossy. The desktop app's clear tool clears after the turn ends, with your approval; in the terminal you type `/clear` yourself.

**A one-time reload mark.** The desktop app's clear restarts the session as a normal startup, so the hook can't tell it from a new chat. `/vault:save` therefore marks the folder in `_System/reload-pending.json` just before clearing. The next session start in that folder reloads the full handoff and removes the mark, and marks older than a week are dropped. Later chats in that folder get only the short pointer, so unrelated work doesn't pay for the handoff.

**Exec-form hook.** The hook runs your configured Python directly with each path as one argument, so paths with spaces need no quoting on any OS.

## Repository layout

The repository root is both the plugin and its marketplace, so the plugin folder is the whole repository.

```
.claude-plugin/marketplace.json   marketplace "maximuse" listing the plugin (source "./")
.claude-plugin/plugin.json        plugin manifest and the three options
hooks/hooks.json                  SessionStart hook (startup|clear|compact)
skills/{save,resume,setup,usage}/SKILL.md
scripts/                          vault_resume.py (hook), vault_find.py, vault_setup.py, usage_sum.py
rules/vault-rules.md              the always-on rules
templates/                        Home.md and _System/Templates/
tests/run_tests.py                script tests in a temp folder
INSTALL.md, TESTING.md            install guide and test plan
```

## Changes

- **0.3.0** – The plugin moved from `plugins/vault/` to the repository root, as Anthropic's directory asks for a plugin whose hook runs a script. Display name is now "Maximuse Vault" (the default vault folder, used only if the option is unset, is now `~/Documents/Maximuse Vault`). Commands, options and vault format are unchanged; existing installs update with `/plugin marketplace update maximuse`, then `/plugin update vault@maximuse`.
- **0.2.0** – `/vault:save` reloads the full handoff after the desktop app's clear, which arrives as a startup rather than `/clear` (it used to load only a pointer).
- **0.1.0** – First release.

## License

MIT
