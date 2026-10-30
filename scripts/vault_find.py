"""Find Maximuse Vault handoffs for the /maximuse:resume and /maximuse:save skills.

Usage: vault_find.py [--vault PATH] [working-directory] [--name TEXT ...]
       vault_find.py [--vault PATH] [working-directory] --mark-reload
Prints the resolved vault, handoffs whose name ("Project / Session") or chat
title (`chat:`) contains TEXT, or every word of it in any order (exact names
first, marked "exact: yes"), the handoff whose `cwd:` matches the folder (if
any), and the most recent (numbered)
unfinished handoffs across the vault, each with its name and note paths.
--mark-reload makes the hook reload the handoff on the folder's next session
start (/maximuse:save runs it right before clearing).
"""
import argparse
import os
import sys
from datetime import datetime

import vault_common as vc

RECENT = 8


def describe(mtime, path, fields):
    session = vc.session_dir(path)
    project = vc.project_dir(path)
    lines = [
        f"  name: {vc.handoff_name(path)}",
        f"  handoff: {path}",
        f"  status: {fields.get('status', 'unknown')} | updated: {datetime.fromtimestamp(mtime):%Y-%m-%d %H:%M}"
        f" | cwd: {fields.get('cwd') or '(empty)'}",
        f"  chat: {fields.get('chat') or '(none)'}",
        f"  project: {project}",
    ]
    for name in ("Brief.md", "Decisions.md", "Gotchas.md"):
        note = os.path.join(project, name)
        lines.append(f"  {name[:-3].lower()}: {note if os.path.isfile(note) else '(missing)'}")
    steps = sorted(n for n in os.listdir(session) if n.endswith(".md") and n != vc.HANDOFF)
    lines.append(f"  step notes: {', '.join(steps) if steps else '(none)'}")
    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault")
    ap.add_argument("--name", nargs="*", default=[])
    ap.add_argument("--mark-reload", action="store_true")
    ap.add_argument("cwd", nargs="?")
    args = ap.parse_args()

    vault = vc.resolve_vault(args.vault)
    raw_cwd = args.cwd or os.getcwd()
    cwd = vc.norm(raw_cwd)
    name = " ".join(args.name).strip()

    print(f"VAULT: {vault}")
    print(f"CWD: {raw_cwd}")
    if not os.path.isdir(vault):
        print("VAULT MISSING: the folder doesn't exist. Run /maximuse:setup first.")
        return
    if args.mark_reload:
        vc.mark_reload(vault, raw_cwd)
        print("RELOAD MARKED: the next session start in this folder reloads its handoff.")
        return
    templates = os.path.join(vault, "_System", "Templates")
    if not os.path.isdir(templates):
        templates = os.path.join(vc.PLUGIN_ROOT, "templates", "_System", "Templates")
    print(f"TEMPLATES: {templates}")

    rows = vc.handoffs(vault)
    if name:
        wanted = name.lower()
        named = [(r, vc.name_match(r[1], r[2], name)) for r in rows]
        named = [(r, how) for r, how in named if how]
        named.sort(key=lambda m: m[1] != "exact")
        print(f"NAME '{name}': {len(named)} match(es)")
        for r, how in named[:5]:
            print(describe(*r))
            if how == "exact":
                print("  exact: yes")
    match = next((r for r in rows if cwd and vc.norm(r[2].get("cwd")) == cwd), None)
    print("MATCH (this folder):" if match else "MATCH: none")
    if match:
        print(describe(*match))

    unfinished = [r for r in rows if r[2].get("status", "").lower() != "done" and r is not match]
    print(f"RECENT UNFINISHED ({len(unfinished)}):" if unfinished else "RECENT UNFINISHED: none")
    for number, (mtime, path, fields) in enumerate(unfinished[:RECENT], 1):
        chat = f" | chat: {fields['chat']}" if fields.get("chat") else ""
        print(f"{number}. {vc.handoff_name(path)} | {fields.get('status', 'unknown')} | updated {datetime.fromtimestamp(mtime):%Y-%m-%d %H:%M}{chat}")


if __name__ == "__main__":
    main()
