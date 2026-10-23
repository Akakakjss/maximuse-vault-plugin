"""Create a Maximuse Vault, or adopt an existing folder as one, and start named handoffs.

Usage: vault_setup.py [--vault PATH] [--dry-run]
       vault_setup.py [--vault PATH] --handoff NAME [--cwd DIR] [--project NAME] [--dry-run]
Copies Home.md and _System/Templates/*.md from the plugin into the vault and
creates Projects/. Existing files are never overwritten, so running it on a
vault you already use only fills in what is missing.
--handoff also creates Projects/<project>/Sessions/<NAME>/00 Handoff.md, named
exactly as given (minus characters Windows forbids in folder names), with
`cwd:` set to DIR. <project> defaults to DIR's folder name, or General for the
home folder. A new project gets its Brief, Decisions and Gotchas and a link in
Home.md. Handoff names are unique across the vault, so an existing one is
reported and left alone.
"""
import argparse
import os
import shutil
import sys
from datetime import datetime

import vault_common as vc

TEMPLATE_ROOT = os.path.join(vc.PLUGIN_ROOT, "templates")


def scaffold(vault, dry_run):
    existed = os.path.isdir(vault)
    had_files = False
    if existed:
        with os.scandir(vault) as entries:
            had_files = any(True for _ in entries)
    created, kept = [], []

    for folder, _, files in os.walk(TEMPLATE_ROOT):
        rel_dir = os.path.relpath(folder, TEMPLATE_ROOT)
        for name in sorted(files):
            rel = os.path.normpath(os.path.join(rel_dir, name))
            dest = os.path.join(vault, rel)
            if os.path.exists(dest):
                kept.append(rel)
                continue
            created.append(rel)
            if not dry_run:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(os.path.join(folder, name), dest)
    projects = os.path.join(vault, "Projects")
    if not os.path.isdir(projects):
        created.append("Projects" + os.sep)
        if not dry_run:
            os.makedirs(projects, exist_ok=True)

    mode = "DRY RUN (nothing written)" if dry_run else ("ADOPTED existing folder" if had_files else "CREATED new vault")
    print(f"{mode}: {vault}")
    print(f"ADDED ({len(created)}): {', '.join(created) if created else 'nothing'}")
    print(f"KEPT AS IS ({len(kept)}): {', '.join(kept) if kept else 'nothing'}")


def project_for(cwd):
    folder = os.path.normpath(os.path.expanduser(cwd))
    if vc.norm(folder) == vc.norm("~") or os.path.dirname(folder) == folder:
        return "General"
    return vc.safe_name(os.path.basename(folder)) or "General"


def from_template(vault, name, now, title=""):
    path = os.path.join(vault, "_System", "Templates", name)
    if not os.path.isfile(path):
        path = os.path.join(TEMPLATE_ROOT, "_System", "Templates", name)
    text = vc.read_text(path)
    return text.replace("{{date}}", f"{now:%Y-%m-%d}").replace("{{time}}", f"{now:%H:%M}").replace("{{title}}", title)


def write_new(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def start_handoff(vault, name, cwd, project, dry_run):
    now = datetime.now()
    taken = [r[1] for r in vc.handoffs(vault) if vc.is_exact_name(r[1], name)]
    if taken:
        print(f"HANDOFF EXISTS: {vc.handoff_name(taken[0])}")
        print(f"  handoff: {taken[0]}")
        return
    project_path = os.path.join(vault, "Projects", project)
    handoff = os.path.join(project_path, "Sessions", name, vc.HANDOFF)
    new_project = not os.path.isdir(project_path)
    project_notes = [n for n in ("Brief.md", "Decisions.md", "Gotchas.md") if not os.path.exists(os.path.join(project_path, n))]
    verb = "WOULD CREATE" if dry_run else "HANDOFF CREATED"
    print(f"{verb}: {project} / {name}")
    print(f"  handoff: {handoff}")
    print(f"  cwd: {cwd}")
    if project_notes:
        print(f"  project notes added: {', '.join(project_notes)}")
    if dry_run:
        return

    text = from_template(vault, "Handoff.md", now)
    head, sep, body = text.partition("\n---\n")
    head = "\n".join(f"cwd: {cwd}" if line.startswith("cwd:") else line for line in head.split("\n"))
    body = body.replace("# Handoff\n", f"# Handoff: {name}\n", 1)
    write_new(handoff, head + sep + body)
    for note in project_notes:
        write_new(os.path.join(project_path, note), from_template(vault, note, now, project))
    if new_project:
        home = os.path.join(vault, "Home.md")
        link = f"- [[Projects/{project}/Brief|{project}]]\n"
        text = vc.read_text(home) if os.path.isfile(home) else "# Maximuse Vault\n\n## Projects\n"
        if link not in text:
            # Add the link at the end of the "## Projects" section, or the end of the note.
            start = text.find("\n## Projects")
            end = text.find("\n## ", start + 1) if start >= 0 else -1
            if end < 0:
                text = text.rstrip("\n") + "\n" + link
            else:
                text = text[:end].rstrip("\n") + "\n" + link + text[end:]
            with open(home, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print("  linked in Home.md under Projects")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--handoff", nargs="*", default=[])
    ap.add_argument("--cwd")
    ap.add_argument("--project")
    args = ap.parse_args()
    vault = vc.resolve_vault(args.vault)

    scaffold(vault, args.dry_run)
    if args.handoff:
        name = vc.safe_name(" ".join(args.handoff))
        cwd = args.cwd or os.getcwd()
        project = vc.safe_name(args.project) or project_for(cwd)
        if not name:
            print("HANDOFF NAME EMPTY: give a name with at least one letter or digit.")
        else:
            start_handoff(vault, name, cwd, project, args.dry_run)
    handoffs = vc.handoffs(vault) if os.path.isdir(vault) else []
    print(f"HANDOFFS FOUND: {len(handoffs)}")


if __name__ == "__main__":
    main()
