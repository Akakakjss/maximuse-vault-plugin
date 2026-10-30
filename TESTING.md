# Test plan

The "Already done" sections below record runs of 0.1.0–0.3.0, when the plugin was called `vault` (commands `/vault:*`, install id `vault@maximuse`). Since 0.4.0 it is `maximuse`; the steps further down use the new names.

Everything here runs in a throwaway profile and a throwaway vault, so your real `~/.claude` and your real vault are never touched.

## Already done (Linux, Claude Code v2.1.301, Python 3)

- `claude plugin validate --strict` passes for the marketplace and the plugin.
- `tests/run_tests.py`: all checks pass (setup create/adopt, hook in every case below, finder, usage summary).
- Real install into a temp `CLAUDE_CONFIG_DIR` from the local marketplace, then `claude --init-only`: with options unset the hook fails with `Plugin option "python" isn't set`; with options set it injects the rules (startup) or the missing-vault notice. A vault path with spaces works.
- Headless `claude -p "/vault:resume login fix"` against a temp vault: the skill's `${user_config.*}` and `${CLAUDE_PLUGIN_ROOT}` references were substituted, the finder found the handoff by name, Claude read the Brief and handoff, checked the folder and tests, and stopped at the permission prompt for writing into the vault (expected: see INSTALL.md, section 5).
- Uninstall and marketplace removal.

## Already done (Windows, 0.1.0, Claude Code v2.1.292, Python 3.14.4)

Run on 2026-10-16 in `C:\cvtest` with `CLAUDE_CONFIG_DIR=C:\cvtest\cfg`; the real profile wasn't touched. `python` on PATH (the Python install manager's alias) works, so the install used `--config python=python`.

- Step 1: `python tests\run_tests.py` → all checks passed, including the Windows case/slash match.
- Step 2: `claude plugin validate --strict` → passed for the marketplace and the plugin.
- Step 3: install with all three `--config` options, then `claude --init-only` → `Hook SessionStart:startup success`, the missing-vault notice (166 chars); after creating the vault and a handoff, 2,637 chars (rules + pointer).
- `vault_setup.py` dry run, create, then adopt the same folder (0 added, 6 kept). `vault_resume.py` with `startup`, `clear` and `compact` input: pointer only on startup; Brief and handoff on clear and compact; ASCII-only JSON with non-ASCII text intact; `c:/CVTEST/work/` still matches; another folder gets rules only.
- Step 11: uninstall → plugin gone, `C:\cvtest\Vault` kept.

## Already done (Windows, 0.2.0, Claude Code v2.1.292, Python 3.14.4)

Run on 2026-10-16 with 0.2.0 installed from GitHub (`claude plugin marketplace add akakakjss/maximuse-vault-plugin`), the same throwaway profile, now logged in, and a fresh vault `C:\cvtest\Vault2`.

- Step 3: `claude --init-only` → `Hook SessionStart:startup (SessionStart) success` with the missing-vault notice; the hook ran from the plugin cache's `0.2.0` folder.
- Step 4: `/vault:setup` created the vault (Home.md and the five templates).
- Step 5: `/vault:save hook test` wrote `work / 2026-10-16 hook test` (`cwd: C:\cvtest\work`) and the reload mark `{"c:/cvtest/work": …}` in `_System\reload-pending.json`.
- Step 5b: `claude --init-only` in `C:\cvtest\work` → "Resuming from the Claude Vault handoff …" (4,418 chars) and the mark was gone; a second `--init-only` → rules + pointer only (2,639 chars).
- Step 6: a live `/clear`, then "what's next": Claude named the handoff, checked `git status` and `git log` first, and proposed the next step.
- Step 7: found the handoff by name from `C:\cvtest\other`, re-pointed `cwd:` there and added a line under "Checked state". Without `--add-dir C:\cvtest\work` it couldn't re-check the repo, so that flag is now in the step.
- Step 8: listed the one unfinished handoff and asked for a name; didn't pick one.
- Step 9: the first run wrote `_System\Usage baseline.md`; the second printed the comparison table.
- Step 10: with `inject_rules` off, the folder with no handoff got no output; the folder with the handoff got a 319-char pointer; after a save (mark) it got the Brief and handoff (2,309 chars). The rules were absent every time.

## Already done (Windows, 0.3.0 root layout)

The plugin moved to the repository root. Installed from the local folder into the same throwaway profile: `claude plugin details vault@maximuse` showed "Maximuse Vault (vault) 0.3.0" with 4 skills and the SessionStart hook. `claude --init-only` in `C:\cvtest\other` gave rules + pointer (2,645 chars); after `--mark-reload`, "Resuming from the Maximuse Vault handoff" (4,635 chars) and the mark was used. The hook ran `scripts/vault_resume.py` from the root.

## Already done (Windows, 0.5.0 named handoffs, Claude Code v2.1.304)

Run on 2026-10-23 in the throwaway profile (`CLAUDE_CONFIG_DIR=C:\cvtest\cfg`, marketplace = the local repo folder on branch `named-handoffs-codex`), fresh vault `C:\cvtest\Vault5`, git repo `C:\cvtest\shop`. Each step was a separate headless `claude -p` session with `--add-dir C:\cvtest\Vault5`.

- `/maximuse:setup checkout redesign` with the vault missing: created the vault, then `Projects\shop\Sessions\checkout redesign\00 Handoff.md` (`cwd: C:\cvtest\shop`, title "Handoff: checkout redesign"), the shop Brief, Decisions and Gotchas, and the Home.md link.
- After a new commit (`bd43697`), `/maximuse:save checkout redesign` in a new session: updated that same folder (no new or renamed folder), added `01 Discount on cart total.md`, wrote the reload mark `{"c:/cvtest/shop": …}`, and asked for `/clear` (no desktop clear tool in the CLI).
- Next session start in `C:\cvtest\shop`: the hook injected "Resuming from the Maximuse Vault handoff"; with no tools, Claude named "shop / checkout redesign", `bd43697` and the next step. The mark was used (`{}`).
- `/maximuse:resume checkout redesign and then just tell me the next step, don't change any files`: took "checkout redesign" as the name and the rest as the request; checked git; changed nothing.

## Already done (Windows, 0.5.0 setup from a task, chat titles)

Run on 2026-10-30 in the same throwaway profile and vault, repo `C:\cvtest\shop3`, headless `claude -p` per step.

- `/maximuse:setup add a tax_rate parameter to cart.total and commit it`: Claude named the handoff `Cart total tax rate` (`chat: Cart total tax rate`), did the task (commit `89662e0`), wrote a step note and set `status: done`. No chat rename in the terminal, as designed.
- `/maximuse:setup "Free shipping rule" add free shipping …`: used the quoted name exactly; commit `7c8c8ed`.
- New session, `/maximuse:resume shipping free rule and then just tell me the commit and next step, don't change any files`: found **shop3 / Free shipping rule** from the reordered words, reported `7c8c8ed`, changed nothing.
- Finder with no name: the unfinished list is numbered (`1. shop2 / codex checkout …`).

## Already done (Windows, 0.5.0 universal install in Codex CLI 0.164.0)

Run on 2026-10-23 in an isolated Codex home (`CODEX_HOME=C:\cvtest\codexhome\.codex`, `HOME` and `USERPROFILE=C:\cvtest\codexhome`, signed in with ChatGPT), shared vault `C:\cvtest\Vault5`, git repo `C:\cvtest\shop2`. Each step was a separate `codex exec -s workspace-write`.

- `install.py --vault C:\cvtest\Vault5 --home … --codex-home … --skills-dir …`: dry run, then install; config.toml got `writable_roots = ['C:\cvtest\Vault5']`.
- First `$maximuse-setup codex checkout`: Codex found the skill but ran `sandbox: read-only` and blocked every command ("blocked by policy"). After adding `[windows] sandbox = "unelevated"`: `sandbox: workspace-write [workdir, /tmp, $TMPDIR, C:\cvtest\Vault5]`, and the script created `Projects\shop2\Sessions\codex checkout\00 Handoff.md`.
- Codex rewrote the handoff with PowerShell `Set-Content -Encoding utf8`, which adds a UTF-8 BOM; the finder then showed `MATCH: none` and status `unknown`. Fixed: notes are read as `utf-8-sig`, with a regression test.
- After a commit (`7fcdb44`), `$maximuse-save codex checkout`: same folder, step note `02`, told the user to start a new chat.
- `$maximuse-resume codex checkout and then just tell me the next step, do not change any files`: name parsed, checks re-run, nothing changed.
- Claude Code (test profile, same vault) ran `/maximuse:resume codex checkout …` and reported the same commit and next step.
- `install.py --uninstall`: removed `.maximuse`, the three skills and the AGENTS.md block; the vault was kept. The real `~/.codex` and `~/.agents` had no Maximuse files at any point.

**Not yet tested:** step 11 (uninstall) on 0.2.0 or later; 0.5.0 in the desktop app (including the chat rename by setup and resume); Codex on macOS/Linux; Cursor or another AGENTS.md tool. The desktop app's `/vault:save` → clear → reload passed with 0.2.0 on the real profile (2026-10-16).

## On the Windows PC

Use short paths (long Windows paths stop Claude Code from starting). PowerShell:

```powershell
# 0. Throwaway profile and folders. You'll be asked to log in once in this profile.
mkdir C:\cvtest\work, C:\cvtest\other
$env:CLAUDE_CONFIG_DIR = "C:\cvtest\cfg"

# 1. Script tests (also checks Windows case/slash matching and cp1252-safe output)
python C:\path\to\maximuse-vault-plugin\tests\run_tests.py

# 2. Install from the local copy
claude plugin validate --strict C:\path\to\maximuse-vault-plugin
claude plugin marketplace add C:\path\to\maximuse-vault-plugin
claude plugin install maximuse@maximuse --config python=python --config vault_path=C:\cvtest\Vault --config inject_rules=true

# 3. Hook through Claude Code, without a conversation
cd C:\cvtest\work
claude --init-only --debug-file C:\cvtest\init.log
Select-String -Path C:\cvtest\init.log -Pattern "SessionStart|additionalContext"
```

Expected in step 3: `provided additionalContext` with the "vault folder … doesn't exist yet" notice, and no `Hook failed`.

Then, still in that PowerShell window (so the throwaway profile is used):

| # | Do | Expect |
|---|---|---|
| 4 | `claude` in `C:\cvtest\work`, then `/maximuse:setup` | Dry-run list, then `CREATED new vault: C:\cvtest\Vault`. |
| 5 | Ask Claude to `git init` and create a small file, then `/maximuse:save hook test` | A session folder `Projects\work\Sessions\<date> hook test\` with `00 Handoff.md` (`cwd: C:\cvtest\work`) and a step note; the message "Handoff saved as **work / <date> hook test**" and the resume command; then a request to type `/clear`. `C:\cvtest\Vault\_System\reload-pending.json` holds `"c:/cvtest/work"`. Don't type `/clear` yet. |
| 5b | In a second PowerShell window with the same `CLAUDE_CONFIG_DIR`: `cd C:\cvtest\work`, `claude --init-only --debug-file C:\cvtest\mark.log`, then `Select-String -Path C:\cvtest\mark.log -Pattern "Resuming from the Maximuse Vault"`. Run `--init-only` once more. | This is what the desktop app's clear looks like (a plain startup). The first run matches "Resuming from the Maximuse Vault handoff" and `reload-pending.json` becomes `{}`; the second run gets only the rules and a pointer. |
| 6 | Back in the first window: type `/clear`, then ask "what's next?" | Claude knows the goal and next step without reading anything, then checks git status before acting. |
| 7 | `cd C:\cvtest\other`, then `claude -p "/maximuse:resume hook test" --max-turns 8 --add-dir C:\cvtest\Vault --add-dir C:\cvtest\work --permission-mode acceptEdits --allowedTools "Bash(python *)" "PowerShell(python *)"` (headless runs can't answer permission prompts; on Windows Claude may run Python through PowerShell) | Finds the handoff by name, re-points its `cwd:` to `C:\cvtest\other` with a note under "Checked state", reports the next step. |
| 8 | `claude -p "/maximuse:resume" --allowedTools "Bash(python *)" "PowerShell(python *)"` | Lists unfinished handoffs and asks which one; doesn't pick one itself. |
| 9 | `/maximuse:usage` twice | First run writes `C:\cvtest\Vault\_System\Usage baseline.md`; second run prints a comparison table. |
| 10 | `/plugin configure maximuse@maximuse` and turn rules off, or from PowerShell: `'{"inject_rules":"false"}' \| claude plugin configure maximuse@maximuse --values-stdin`. Then start a new session. | No rules at startup; after `/clear` (or a save) in a folder with a handoff, only the Brief and handoff. |
| 11 | `claude plugin uninstall maximuse@maximuse` | Plugin gone; `C:\cvtest\Vault` still there. |

Clean up: close the window (or `Remove-Item Env:CLAUDE_CONFIG_DIR`) and delete `C:\cvtest`.

## Desktop app

The desktop app uses your real profile, so test it after [moving from the personal setup](INSTALL.md#moving-from-the-personal-setup):

1. In a desktop chat with some work in it, run `/maximuse:save desktop test`.
2. Approve the clear prompt. Expect the chat to clear after Claude's turn and the next message to continue from the handoff. The app restarts the session as a plain startup, so the full reload relies on the mark `/maximuse:save` writes just before clearing (0.2.0): Claude should know the next step without opening any notes. If it only knows that a handoff exists, the mark wasn't written or was used up by another session start in that folder.
3. If the clear tool is missing or refused, Claude should fall back to asking you to type `/clear`.
4. If a desktop session shows `Plugin option ... isn't set`, set the options from the terminal (INSTALL.md, section 2) and start a new desktop session.

This is the first live run of `save` with the clear tool, so note whether the tool name `mcp__ccd_session_mgmt__clear_session` still matches what the app offers; if it changed, update `skills/save/SKILL.md`.
