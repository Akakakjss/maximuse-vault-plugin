"""SessionStart hook for the Maximuse Vault plugin.

Every session (startup, /clear, compaction) it can add the short note rules.
On /clear, compaction, or the first start after /vault:save marked the folder,
it also adds the project's Brief.md and the newest 00 Handoff.md whose `cwd:`
matches the session's folder; on other startups it only points to that handoff.
The mark exists because the desktop app's clear starts the session as
"startup". Output is ASCII-safe JSON on stdout.

Claude Code moves additionalContext over 10,000 characters into a file and
shows Claude only a preview, so everything here is kept under MAX_CONTEXT.
"""
import argparse
import json
import os
import sys
from datetime import datetime

import vault_common as vc

MAX_CONTEXT = 9500
RULES_FILE = os.path.join(vc.PLUGIN_ROOT, "rules", "vault-rules.md")


def rules_text(vault):
    text = vc.read_text(RULES_FILE)
    # Drop the file's own comment header (lines before the first heading).
    start = text.find("\n# ")
    text = text[start + 1:] if start >= 0 else text
    return text.replace("{{VAULT}}", vault).strip()


def clip(text, limit, path):
    if len(text) <= limit:
        return text
    note = f"\n\n[truncated; read the full note at {path}]"
    return text[: max(0, limit - len(note))] + note


def build(data, vault, inject_rules):
    source = data.get("source") or "startup"
    cwd = vc.norm(data.get("cwd") or os.getcwd())
    parts = []

    if not os.path.isdir(vault):
        return (
            f"Maximuse Vault plugin: the vault folder {vault} doesn't exist yet, so no notes are kept. "
            "The user can run /vault:setup to create it or adopt an existing folder."
        )

    if inject_rules:
        parts.append(rules_text(vault))

    reload = vc.take_reload(vault, cwd) or source in ("clear", "compact")
    match = next((r for r in vc.handoffs(vault) if cwd and vc.norm(r[2].get("cwd")) == cwd), None)
    if match:
        mtime, path, fields = match
        status = (fields.get("status") or "unknown").lower()
        updated = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        name = vc.handoff_name(path)
        if status == "done":
            pass
        elif reload:
            header = (
                f"Resuming from the Maximuse Vault handoff \"{name}\" ({vault}). The resume steps in the "
                "vault rules apply: check the real state first, restate the next step, honor \"Don't retry\"."
            )
            brief_path = os.path.join(vc.project_dir(path), "Brief.md")
            brief = vc.read_text(brief_path) if os.path.isfile(brief_path) else ""
            handoff = vc.read_text(path)
            brief_title = f"=== {brief_path} ===\n"
            handoff_title = f"=== {path} (updated {updated}) ===\n"
            # Fixed text: earlier parts, header, titles and the "\n\n" joins.
            fixed = sum(len(p) + 2 for p in parts) + len(header) + len(handoff_title) + 2
            if brief:
                fixed += len(brief_title) + 2
            room = MAX_CONTEXT - fixed
            # The handoff gets priority; the Brief gets what is left (at least a pointer).
            handoff = clip(handoff, max(1000, room - min(len(brief), 2500)), path)
            room -= len(handoff)
            section = [header]
            if brief:
                section.append(brief_title + clip(brief, max(200, room), brief_path))
            section.append(handoff_title + handoff)
            parts.append("\n\n".join(section))
        else:
            parts.append(
                f"Maximuse Vault: an unfinished handoff \"{name}\" exists for this folder: {path} "
                f"(status: {status}, updated {updated}). If the user's request continues that work, "
                "read it and the project's Brief.md first; otherwise ignore it."
            )

    context = "\n\n".join(parts)
    return context[:MAX_CONTEXT]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault")
    ap.add_argument("--rules")
    args, _ = ap.parse_known_args()
    vault = vc.resolve_vault(args.vault)
    inject = vc.parse_bool(args.rules if args.rules is not None else os.environ.get("CLAUDE_PLUGIN_OPTION_INJECT_RULES"))

    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    data = json.loads(raw) if raw.strip() else {}
    context = build(data, vault, inject)
    if context:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never let a notes problem block a session from starting.
        if os.environ.get("CLAUDE_VAULT_DEBUG"):
            raise
