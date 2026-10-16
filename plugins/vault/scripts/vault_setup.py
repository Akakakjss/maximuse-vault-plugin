"""Create a Claude Vault, or adopt an existing folder as one.

Usage: vault_setup.py [--vault PATH] [--dry-run]
Copies Home.md and _System/Templates/*.md from the plugin into the vault and
creates Projects/. Existing files are never overwritten, so running it on a
vault you already use only fills in what is missing.
"""
import argparse
import os
import shutil
import sys

import vault_common as vc

TEMPLATE_ROOT = os.path.join(vc.PLUGIN_ROOT, "templates")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    vault = vc.resolve_vault(args.vault)

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
            if not args.dry_run:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(os.path.join(folder, name), dest)
    projects = os.path.join(vault, "Projects")
    if not os.path.isdir(projects):
        created.append("Projects" + os.sep)
        if not args.dry_run:
            os.makedirs(projects, exist_ok=True)

    mode = "DRY RUN (nothing written)" if args.dry_run else ("ADOPTED existing folder" if had_files else "CREATED new vault")
    print(f"{mode}: {vault}")
    print(f"ADDED ({len(created)}): {', '.join(created) if created else 'nothing'}")
    print(f"KEPT AS IS ({len(kept)}): {', '.join(kept) if kept else 'nothing'}")
    handoffs = vc.handoffs(vault) if os.path.isdir(vault) else []
    print(f"HANDOFFS FOUND: {len(handoffs)}")


if __name__ == "__main__":
    main()
