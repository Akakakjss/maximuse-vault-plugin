r"""Install Maximuse for Codex and other agents that read AGENTS.md.

Usage:
    python universal/install.py --vault "<vault folder>" [--dry-run]
    python universal/install.py --vault "<vault folder>" --project "<repo>"   (also that repo's AGENTS.md)
    python universal/install.py --uninstall [--project "<repo>"]

What it writes (nothing else is touched):
  <home>/scripts, <home>/templates      the vault scripts and note templates (home: ~/.maximuse)
  <home>/skills/maximuse-*/SKILL.md     the setup, save and resume instructions, paths filled in
  <skills dir>/maximuse-*/SKILL.md      the same, where Codex finds skills (~/.agents/skills)
  <codex home>/AGENTS.md                the always-on rules, between maximuse markers (~/.codex)
  <repo>/AGENTS.md                      the same rules, for each --project
and creates or adopts the vault (it never overwrites a note). Reinstalling
replaces only what it wrote. --uninstall removes it all again; the vault and
the rest of each AGENTS.md are kept.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
START = "<!-- maximuse:start (written by Maximuse install.py; reinstalling replaces this block) -->"
START_PREFIX = "<!-- maximuse:start"
END = "<!-- maximuse:end -->"
SKILLS = ("maximuse-setup", "maximuse-save", "maximuse-resume")
SCRIPTS = ("vault_common.py", "vault_find.py", "vault_setup.py")
CODEX_LIMIT = 32 * 1024


def say(dry, verb, path):
    print(f"{'WOULD ' + verb if dry else verb}: {path}")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text, dry):
    say(dry, "WRITE", path)
    if not dry:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def fill(text, values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def rules_block(values):
    text = read(os.path.join(HERE, "rules.md"))
    start = text.find("\n# ")
    text = text[start + 1:] if start >= 0 else text
    return f"{START}\n{fill(text, values).strip()}\n{END}"


def strip_block(text):
    """Text with the maximuse block (and the blank lines around it) removed."""
    start = text.find(START_PREFIX)
    end = text.find(END, start)
    if start < 0 or end < 0:
        return text
    return (text[:start].rstrip("\n") + "\n\n" + text[end + len(END):].lstrip("\n")).strip("\n") + "\n"


def put_block(path, block, dry):
    old = read(path) if os.path.isfile(path) else ""
    rest = strip_block(old).strip("\n") if old.strip() else ""
    text = (rest + "\n\n" if rest else "") + block + "\n"
    write(path, text, dry)
    if len(text.encode("utf-8")) > CODEX_LIMIT:
        print(f"  note: {path} is over 32 KiB; Codex stops reading AGENTS.md files past project_doc_max_bytes")


def drop_block(path, dry):
    if not os.path.isfile(path):
        return
    old = read(path)
    if START_PREFIX not in old:
        return
    text = strip_block(old)
    if text.strip():
        write(path, text, dry)
    else:
        say(dry, "REMOVE", path)
        if not dry:
            os.remove(path)


def remove_tree(path, dry):
    if os.path.isdir(path):
        say(dry, "REMOVE", path)
        if not dry:
            shutil.rmtree(path)


def agents_files(args):
    files = [] if args.no_codex else [os.path.join(args.codex_home, "AGENTS.md")]
    return files + [os.path.join(os.path.abspath(os.path.expanduser(p)), "AGENTS.md") for p in args.project]


def install(args):
    vault = os.path.normpath(os.path.expanduser(args.vault))
    home = args.home
    values = {"VAULT": vault, "PYTHON": args.python, "HOME": home.replace("\\", "/")}
    dry = args.dry_run

    for name in SCRIPTS:
        src = os.path.join(REPO, "scripts", name)
        say(dry, "COPY", os.path.join(home, "scripts", name))
        if not dry:
            os.makedirs(os.path.join(home, "scripts"), exist_ok=True)
            shutil.copyfile(src, os.path.join(home, "scripts", name))
    say(dry, "COPY", os.path.join(home, "templates"))
    if not dry:
        shutil.rmtree(os.path.join(home, "templates"), ignore_errors=True)
        shutil.copytree(os.path.join(REPO, "templates"), os.path.join(home, "templates"))

    for skill in SKILLS:
        text = fill(read(os.path.join(HERE, "skills", skill, "SKILL.md")), values)
        for root in (os.path.join(home, "skills"), args.skills_dir):
            write(os.path.join(root, skill, "SKILL.md"), text, dry)

    block = rules_block(values)
    for path in agents_files(args):
        put_block(path, block, dry)

    print()
    cmd = [sys.executable, os.path.join(REPO, "scripts", "vault_setup.py"), "--vault", vault] + (["--dry-run"] if dry else [])
    subprocess.run(cmd, check=False)
    print()
    print("Done." if not dry else "Dry run: nothing was written.")
    print("Codex: start a new chat and type $maximuse-setup <name>; later $maximuse-save <name> and $maximuse-resume <name>.")
    print("Other AGENTS.md tools: type 'maximuse setup <name>', 'maximuse save <name>', 'maximuse resume <name>'.")
    print("To let Codex write notes without asking, add the vault to ~/.codex/config.toml:")
    print("  [sandbox_workspace_write]")
    # A TOML literal string ('...') keeps Windows backslashes as they are.
    print(f"  writable_roots = ['{vault}']")


def uninstall(args):
    dry = args.dry_run
    for path in agents_files(args):
        drop_block(path, dry)
    for skill in SKILLS:
        remove_tree(os.path.join(args.skills_dir, skill), dry)
    remove_tree(args.home, dry)
    print("Removed." if not dry else "Dry run: nothing was removed.")
    print("Your vault and the rest of each AGENTS.md were not touched.")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Install Maximuse for Codex and other AGENTS.md agents.")
    ap.add_argument("--vault", help="vault folder to create or adopt (required to install)")
    ap.add_argument("--python", default=sys.executable, help="Python 3 the skills run (default: this one)")
    ap.add_argument("--home", default=os.path.join("~", ".maximuse"), help="where scripts and skills go (default ~/.maximuse)")
    ap.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or os.path.join("~", ".codex"))
    ap.add_argument("--skills-dir", default=os.path.join("~", ".agents", "skills"), help="Codex's user skills folder")
    ap.add_argument("--project", action="append", default=[], help="also add the rules to this folder's AGENTS.md")
    ap.add_argument("--no-codex", action="store_true", help="don't touch the global Codex AGENTS.md")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for key in ("home", "codex_home", "skills_dir"):
        setattr(args, key, os.path.abspath(os.path.expanduser(getattr(args, key))))

    if args.uninstall:
        uninstall(args)
    elif not args.vault:
        ap.error("--vault is required to install")
    else:
        install(args)


if __name__ == "__main__":
    main()
