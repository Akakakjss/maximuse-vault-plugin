"""Shared helpers for the Claude Vault plugin scripts.

The vault folder is resolved in this order:
  1. --vault PATH on the command line (skills and the hook pass the plugin's
     vault_path option this way)
  2. the CLAUDE_VAULT environment variable
  3. CLAUDE_PLUGIN_OPTION_VAULT_PATH (Claude Code exports it to hook processes)
  4. the default, ~/Documents/Claude Vault
A value that still contains an unsubstituted "${" placeholder is ignored.
"""
import glob
import os

DEFAULT_VAULT = os.path.join("~", "Documents", "Claude Vault")
HANDOFF = "00 Handoff.md"
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
