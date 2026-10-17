"""Shared helpers for the Maximuse Vault plugin scripts.

The vault folder is resolved in this order:
  1. --vault PATH on the command line (skills and the hook pass the plugin's
     vault_path option this way)
  2. the CLAUDE_VAULT environment variable
  3. CLAUDE_PLUGIN_OPTION_VAULT_PATH (Claude Code exports it to hook processes)
  4. the default, ~/Documents/Maximuse Vault
A value that still contains an unsubstituted "${" placeholder is ignored.
"""
import glob
import json
import os
import time

DEFAULT_VAULT = os.path.join("~", "Documents", "Maximuse Vault")
HANDOFF = "00 Handoff.md"
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELOAD_FILE = os.path.join("_System", "reload-pending.json")
RELOAD_MAX_AGE = 7 * 24 * 3600


def _usable(value):
    value = (value or "").strip().strip("\"'")
    return value if value and "${" not in value else ""


def resolve_vault(cli_value=None):
    for value in (cli_value, os.environ.get("CLAUDE_VAULT"), os.environ.get("CLAUDE_PLUGIN_OPTION_VAULT_PATH")):
        value = _usable(value)
        if value:
            break
    else:
        value = DEFAULT_VAULT
    return os.path.normpath(os.path.expanduser(value))


def parse_bool(value, default=True):
    value = _usable(value).lower()
    if not value:
        return default
    return value not in ("0", "false", "no", "off")


def norm(path):
    """Normalize a folder path for comparison: case-insensitive on Windows, slashes unified."""
    path = _usable(path)
    if not path:
        return ""
    path = os.path.normpath(os.path.expanduser(path)).rstrip("\\/") or os.sep
    return os.path.normcase(path).replace("\\", "/").lower() if os.name == "nt" else path


def frontmatter(path):
    fields = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        if f.readline().strip() != "---":
            return fields
        for line in f:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip()] = value.strip()
    return fields


def handoffs(vault):
    """Every handoff in the vault as (mtime, path, frontmatter), newest first."""
    rows = []
    for path in glob.glob(os.path.join(glob.escape(vault), "Projects", "**", HANDOFF), recursive=True):
        try:
            rows.append((os.path.getmtime(path), path, frontmatter(path)))
        except OSError:
            continue
    rows.sort(key=lambda r: r[0], reverse=True)
    return rows


def session_dir(handoff_path):
    return os.path.dirname(handoff_path)


def project_dir(handoff_path):
    # Projects/<Project>/Sessions/<session>/00 Handoff.md
    return os.path.dirname(os.path.dirname(session_dir(handoff_path)))


def handoff_name(handoff_path):
    return f"{os.path.basename(project_dir(handoff_path))} / {os.path.basename(session_dir(handoff_path))}"


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


# /maximuse:save marks its folder before clearing, because the desktop app's clear
# restarts the session as "startup", not "clear". The hook's next start in that
# folder takes the mark and reloads the handoff as after a clear, once.
def _reload_marks(vault):
    try:
        with open(os.path.join(vault, RELOAD_FILE), encoding="utf-8") as f:
            marks = json.load(f)
        return marks if isinstance(marks, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_reload_marks(vault, marks):
    path = os.path.join(vault, RELOAD_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(marks, f, indent=1)


def mark_reload(vault, cwd):
    marks = _reload_marks(vault)
    marks[norm(cwd)] = time.time()
    _write_reload_marks(vault, marks)


def take_reload(vault, cwd):
    """Remove this folder's reload mark (and marks older than a week); True if it had one."""
    marks = _reload_marks(vault)
    cwd = norm(cwd)
    now = time.time()
    keep = {k: v for k, v in marks.items() if k != cwd and isinstance(v, (int, float)) and now - v < RELOAD_MAX_AGE}
    if keep != marks:
        _write_reload_marks(vault, keep)
    return bool(cwd) and cwd in marks
