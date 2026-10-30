# Installing Maximuse Vault

## 1. Before you start

- **Python 3.8 or later.** Check it in a terminal: `python --version` on Windows, `python3 --version` on macOS and Linux. On Windows, if `python` opens the Microsoft Store, install Python from python.org or use the full path to `python.exe`.
- **Obsidian** is optional. The vault is plain Markdown; Obsidian just makes the `[[links]]` clickable.
- **Already running the personal (non-plugin) version on this machine?** Read [Moving from the personal setup](#moving-from-the-personal-setup) first, or you'll get every rule and handoff twice.

## 2. Add the marketplace and install

In Claude Code (terminal or desktop app):

```
/plugin marketplace add akakakjss/maximuse-vault-plugin
/plugin install maximuse@maximuse
```

To try it from a local copy before it's on GitHub, give the folder instead: `/plugin marketplace add C:\path\to\maximuse-vault-plugin` (Windows) or `/plugin marketplace add ~/maximuse-vault-plugin`.

The install opens a dialog with three options. **Fill in all three**: an option you leave unset makes the hook fail at every session start with `Plugin option "python" isn't set`. The defaults in the manifest are not applied on their own (checked with Claude Code v2.1.301).

| Option | What to enter |
|---|---|
| Vault folder (`vault_path`) | Where the vault lives or should be created. Windows example: `C:\Users\you\Documents\Maximuse Vault`. macOS/Linux: `~/Documents/Maximuse Vault`. If your Documents folder is synced by OneDrive, use the path you actually see in Explorer. |
| Python 3 command (`python`) | `python` on Windows (or the full path to `python.exe`), `python3` on macOS and Linux. |
| Load the note rules every session (`inject_rules`) | On. Turn it off only if you paste the rules into your own CLAUDE.md (see [Design notes](README.md#design-notes)). |

From a shell instead, set the options on the install command (the shell install never shows the dialog):

```
claude plugin marketplace add akakakjss/maximuse-vault-plugin
claude plugin install maximuse@maximuse --config python=python --config "vault_path=C:\Users\you\Documents\Maximuse Vault" --config inject_rules=true
```

Change them later with `/plugin configure maximuse@maximuse`, or from a shell by piping JSON to `claude plugin configure maximuse@maximuse --values-stdin` (for example `{"inject_rules":"false"}`; options you leave out keep their values). `claude plugin configure maximuse@maximuse` on its own lists the options and whether each is set. The terminal, the desktop app's local sessions and VS Code read the same settings, so options set in one apply to all; if the desktop app's plugin browser doesn't ask for the options, set them from the terminal as above. Restart Claude Code (or start a new session) after installing or changing options.

## 3. First run

Start a new session and run:

```
/maximuse:setup
```

It shows what it will create, then creates `Home.md`, `_System/Templates/` and `Projects/`. Pointing it at a folder you already use as a vault only adds the missing pieces; it never overwrites a file. Open the folder in Obsidian ("Open folder as vault") if you use Obsidian.

Then start each piece of work by telling Claude what to do:

```
/maximuse:setup add discount codes to the cart
```

Claude names the handoff from the task (for example `Cart discount codes`), creates `Projects/<this folder's name>/Sessions/Cart discount codes/00 Handoff.md`, renames the desktop chat to `Cart discount codes`, and starts the work. To pick the name yourself, put it in quotes first: `/maximuse:setup "checkout redesign" add discount codes`. Later, `/maximuse:save` updates that same handoff and clears the chat, and in any new chat `/maximuse:resume Cart discount codes` (the old chat's title, as the sidebar shows it) continues it. `/maximuse:resume` on its own lists unfinished handoffs by number. (Text that looks like a folder path, such as `/maximuse:setup D:\Notes\Vault`, sets up the vault there instead.)

## 4. Everyday use

| Command | When |
|---|---|
| `/maximuse:setup <what you want done>` | You start a piece of work. Names the handoff (and the desktop chat) from the task, then starts. |
| `/maximuse:save` | The chat is getting long (Claude suggests it around 250k tokens) or you're stepping away. Writes the notes into this chat's handoff, then clears. |
| `/maximuse:resume <chat name> [what next]` | You're in a new chat and want to continue earlier work: type the old chat's title or part of the handoff's name, optionally followed by what to do. With nothing, it lists unfinished handoffs by number and asks. |
| `/maximuse:usage` | You want to see whether it's working. The first run saves a baseline; later runs compare with it. |

Claude also writes short step notes on its own after commits, passing tests, decisions and finished requests.

**How `save` clears the chat**

- **Desktop app:** Claude calls the app's clear tool, which asks you to approve. The chat clears when Claude's turn ends; the hook reloads the Brief and handoff, and your next message continues from them. The app restarts the session as a normal start, so `save` leaves a one-time mark in `_System/reload-pending.json` just before clearing to tell the hook to reload.
- **Terminal:** Claude saves the notes and asks you to type `/clear` yourself. Use `/clear`, not `/compact`: compaction replaces the conversation with a lossy summary, while the handoff was built to be resumed from.
- Either way, `save` prints the resume command, e.g. `/maximuse:resume login fix`, which works from any other chat or folder.

## 5. Permissions you'll see

- **At install:** Claude Code asks you to trust the plugin. The plugin's hook then runs your configured Python with `vault_resume.py` at every session start, `/clear` and compaction, without asking. It reads the vault and prints text for Claude, and uses no network. The only file it writes is `_System/reload-pending.json` in the vault, where it removes the reload mark that `/maximuse:save` left (and marks older than a week).
- **Running the scripts:** the first time Claude runs `vault_find.py`, `vault_setup.py` or `usage_sum.py`, you get a Bash permission prompt. "Yes, and don't ask again" is fine for these.
- **Writing notes:** the vault is usually outside your project folder, so Claude asks before each write there. To allow it once and for all, add the vault to your user settings (`~/.claude/settings.json`), adjusting the path:

  ```json
  {
    "permissions": {
      "additionalDirectories": ["~/Documents/Maximuse Vault"],
      "allow": ["Read(~/Documents/Maximuse Vault/**)", "Edit(~/Documents/Maximuse Vault/**)"]
    }
  }
  ```

  On Windows, a path outside your home folder is written like `//d/Notes/Maximuse Vault/**`.
- **Clearing in the desktop app:** the clear tool asks for approval every time. In **auto mode** it isn't asked at all: auto mode's safety check blocks it ("denied by the Claude Code auto mode classifier"), and `save` falls back to asking you to type `/clear`. To let `save` clear the chat in auto mode too, allow the tool in `~/.claude/settings.json`:

  ```json
  {
    "permissions": {
      "allow": ["mcp__ccd_session_mgmt__clear_session"]
    }
  }
  ```

  Trade-off: Claude can then clear its own chat without a prompt. Only `save` uses the tool, the handoff is always written first, and the old transcript stays on disk.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `SessionStart hook error` mentioning `Plugin option "python" isn't set` (or `vault_path`, `inject_rules`) | Set all three options with `/plugin configure maximuse@maximuse`, then restart. |
| Hook error saying the command can't be found or spawned | The Python option doesn't name a real executable. Use `python` (Windows) or `python3`, or the full path. On Windows it must be a real `.exe`, not a `.bat`/`.cmd` shim. |
| Nothing loads after `/clear` | The handoff's `cwd:` must be this exact folder (case and slashes don't matter on Windows). Run `/maximuse:resume <name>` once in this folder; it re-points the handoff. Handoffs with `status: done` are never reloaded. |
| Desktop app: `save` says the clear was blocked or "denied by the Claude Code auto mode classifier" | Auto mode blocks the clear tool. Type `/clear` yourself, leave auto mode before saving, or allow the tool (section 5). |
| Desktop app: the chat cleared but nothing reloaded yet | A cleared chat starts its new session, and runs the hook, only when you send the next message. Send one; the handoff loads then. |
| "The vault folder … doesn't exist yet" at every start | Run `/maximuse:setup`, or fix the Vault folder option. |
| Rules or handoff appear twice | The personal setup is still installed. See the next section. |
| Claude says the handoff was cut off | The hook loads at most about 9,500 characters in all; Claude Code would otherwise show only a preview. Claude reads the full note from the path given. Keep handoffs short; the save skill aims for under 6,000 characters. |
| Claude Code won't start in a test folder (Windows) | Very long Windows paths break startup. Use a short folder such as `C:\cvtest`. |
| Debugging the hook | Start with `claude --debug-file hook.log` and search the log for `SessionStart`. Setting the environment variable `CLAUDE_VAULT_DEBUG=1` makes script errors visible instead of silent. |

## 7. Uninstall

```
/plugin uninstall maximuse@maximuse
/plugin marketplace remove maximuse
```

(or `claude plugin uninstall maximuse@maximuse` and `claude plugin marketplace remove maximuse` in a shell). This removes the plugin, its hook and its options. **Your vault folder is not touched**; delete it yourself if you no longer want the notes. Remove any vault permission rules you added to `settings.json`.

## Moving from the personal setup

If you used the hand-installed version (a `vault_resume.py` hook in `~/.claude/settings.json`, a `~/.claude/skills/vault/` skill and a "Claude Vault" section in `~/.claude/CLAUDE.md`), both would run side by side. Before enabling the plugin:

1. Back up `~/.claude/settings.json`, `~/.claude/CLAUDE.md` and `~/.claude/skills/vault/`.
2. Remove the `SessionStart` entry that runs `vault_resume.py` from `settings.json`.
3. Move `~/.claude/skills/vault/` out of `~/.claude/skills/` (otherwise `/vault` and `/maximuse:*` both exist).
4. Remove the "Claude Vault" section from CLAUDE.md, or keep it and turn the plugin's rules option off.
5. Install the plugin with the Vault folder option set to your existing vault, then run `/maximuse:setup` on it: it adds nothing you already have, and existing handoffs keep working because the note format is unchanged.

To try the plugin without touching your real profile first, see [TESTING.md](TESTING.md).
