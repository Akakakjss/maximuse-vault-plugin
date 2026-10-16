# Installing Claude Vault

## 1. Before you start

- **Python 3.8 or later.** Check it in a terminal: `python --version` on Windows, `python3 --version` on macOS and Linux. On Windows, if `python` opens the Microsoft Store, install Python from python.org or use the full path to `python.exe`.
- **Obsidian** is optional. The vault is plain Markdown; Obsidian just makes the `[[links]]` clickable.
- **Already running the personal (non-plugin) version on this machine?** Read [Moving from the personal setup](#moving-from-the-personal-setup) first, or you'll get every rule and handoff twice.

## 2. Add the marketplace and install

In Claude Code (terminal or desktop app):

```
/plugin marketplace add <github-owner>/<repo>
/plugin install vault@maximuse
```

To try it from a local copy before it's on GitHub, give the folder instead: `/plugin marketplace add C:\path\to\maximuse-vault-plugin` (Windows) or `/plugin marketplace add ~/maximuse-vault-plugin`.

The install opens a dialog with three options. **Fill in all three**: an option you leave unset makes the hook fail at every session start with `Plugin option "python" isn't set`. The defaults in the manifest are not applied on their own (checked with Claude Code v2.1.301).

| Option | What to enter |
|---|---|
| Vault folder (`vault_path`) | Where the vault lives or should be created. Windows example: `C:\Users\you\Documents\Claude Vault`. macOS/Linux: `~/Documents/Claude Vault`. If your Documents folder is synced by OneDrive, use the path you actually see in Explorer. |
| Python 3 command (`python`) | `python` on Windows (or the full path to `python.exe`), `python3` on macOS and Linux. |
| Load the note rules every session (`inject_rules`) | On. Turn it off only if you paste the rules into your own CLAUDE.md (see [Design notes](README.md#design-notes)). |

From a shell instead, set the options on the install command (the shell install never shows the dialog):

```
claude plugin marketplace add <github-owner>/<repo>
claude plugin install vault@maximuse --config python=python --config "vault_path=C:\Users\you\Documents\Claude Vault" --config inject_rules=true
```

Change them later with `/plugin configure vault@maximuse`. The terminal, the desktop app's local sessions and VS Code read the same settings, so options set in one apply to all; if the desktop app's plugin browser doesn't ask for the options, set them from the terminal as above. Restart Claude Code (or start a new session) after installing or changing options.

## 3. First run

Start a new session and run:

```
/vault:setup
```

It shows what it will create, then creates `Home.md`, `_System/Templates/` and `Projects/`. Pointing it at a folder you already use as a vault only adds the missing pieces; it never overwrites a file. Open the folder in Obsidian ("Open folder as vault") if you use Obsidian.

## 4. Everyday use

| Command | When |
|---|---|
| `/vault:save [name]` | The chat is getting long (Claude suggests it around 250k tokens) or you're stepping away. Writes the notes, then clears. |
| `/vault:resume <part of name>` | You're in a new chat and want to continue earlier work. With no name, it lists unfinished handoffs and asks. |
| `/vault:usage` | You want to see whether it's working. The first run saves a baseline; later runs compare with it. |

Claude also writes short step notes on its own after commits, passing tests, decisions and finished requests.

**How `save` clears the chat**

- **Desktop app:** Claude calls the app's clear tool, which asks you to approve. The chat clears when Claude's turn ends; the hook reloads the Brief and handoff, and your next message continues from them.
- **Terminal:** Claude saves the notes and asks you to type `/clear` yourself. Use `/clear`, not `/compact`: compaction replaces the conversation with a lossy summary, while the handoff was built to be resumed from.
- Either way, `save` prints the resume command, e.g. `/vault:resume login fix`, which works from any other chat or folder.

## 5. Permissions you'll see

- **At install:** Claude Code asks you to trust the plugin. The plugin's hook then runs your configured Python with `vault_resume.py` at every session start, `/clear` and compaction, without asking. It only reads the vault and prints text for Claude; it writes nothing and uses no network.
- **Running the scripts:** the first time Claude runs `vault_find.py`, `vault_setup.py` or `usage_sum.py`, you get a Bash permission prompt. "Yes, and don't ask again" is fine for these.
- **Writing notes:** the vault is usually outside your project folder, so Claude asks before each write there. To allow it once and for all, add the vault to your user settings (`~/.claude/settings.json`), adjusting the path:

  ```json
  {
    "permissions": {
      "additionalDirectories": ["~/Documents/Claude Vault"],
      "allow": ["Read(~/Documents/Claude Vault/**)", "Edit(~/Documents/Claude Vault/**)"]
    }
  }
  ```

  On Windows, a path outside your home folder is written like `//d/Notes/Claude Vault/**`.
- **Clearing in the desktop app:** the clear tool asks for approval every time.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `SessionStart hook error` mentioning `Plugin option "python" isn't set` (or `vault_path`, `inject_rules`) | Set all three options with `/plugin configure vault@maximuse`, then restart. |
| Hook error saying the command can't be found or spawned | The Python option doesn't name a real executable. Use `python` (Windows) or `python3`, or the full path. On Windows it must be a real `.exe`, not a `.bat`/`.cmd` shim. |
| Nothing loads after `/clear` | The handoff's `cwd:` must be this exact folder (case and slashes don't matter on Windows). Run `/vault:resume <name>` once in this folder; it re-points the handoff. Handoffs with `status: done` are never reloaded. |
| "The vault folder … doesn't exist yet" at every start | Run `/vault:setup`, or fix the Vault folder option. |
| Rules or handoff appear twice | The personal setup is still installed. See the next section. |
| Claude says the handoff was cut off | The hook loads at most about 9,500 characters in all; Claude Code would otherwise show only a preview. Claude reads the full note from the path given. Keep handoffs short; the save skill aims for under 6,000 characters. |
| Claude Code won't start in a test folder (Windows) | Very long Windows paths break startup. Use a short folder such as `C:\cvtest`. |
| Debugging the hook | Start with `claude --debug-file hook.log` and search the log for `SessionStart`. Setting the environment variable `CLAUDE_VAULT_DEBUG=1` makes script errors visible instead of silent. |

## 7. Uninstall

```
/plugin uninstall vault@maximuse
/plugin marketplace remove maximuse
```

(or `claude plugin uninstall vault@maximuse` and `claude plugin marketplace remove maximuse` in a shell). This removes the plugin, its hook and its options. **Your vault folder is not touched**; delete it yourself if you no longer want the notes. Remove any vault permission rules you added to `settings.json`.

## Moving from the personal setup

If you used the hand-installed version (a `vault_resume.py` hook in `~/.claude/settings.json`, a `~/.claude/skills/vault/` skill and a "Claude Vault" section in `~/.claude/CLAUDE.md`), both would run side by side. Before enabling the plugin:

1. Back up `~/.claude/settings.json`, `~/.claude/CLAUDE.md` and `~/.claude/skills/vault/`.
2. Remove the `SessionStart` entry that runs `vault_resume.py` from `settings.json`.
3. Move `~/.claude/skills/vault/` out of `~/.claude/skills/` (otherwise `/vault` and `/vault:*` both exist).
4. Remove the "Claude Vault" section from CLAUDE.md, or keep it and turn the plugin's rules option off.
5. Install the plugin with the Vault folder option set to your existing vault, then run `/vault:setup` on it: it adds nothing you already have, and existing handoffs keep working because the note format is unchanged.

To try the plugin without touching your real profile first, see [TESTING.md](TESTING.md).
