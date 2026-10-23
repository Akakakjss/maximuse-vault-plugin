r"""Self-contained tests for the Maximuse Vault plugin scripts.

Run with the same Python the plugin is configured to use:
    python tests/run_tests.py            (Windows)
    python3 tests/run_tests.py           (macOS / Linux)

Everything happens in a temporary folder; your real vault and ~/.claude are
never touched. Hook input JSON is generated here in Python, so there is no
shell quoting of backslashes to get wrong (Git Bash collapses \\ to \).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
INSTALL = os.path.join(os.path.dirname(HERE), "universal", "install.py")
PY = sys.executable
FAILS = []


def run(script, args=(), stdin=b"", env=None):
    full_env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE_VAULT", "CLAUDE_PLUGIN_OPTION_"))}
    full_env.update(env or {})
    p = subprocess.run([PY, os.path.join(SCRIPTS, script), *args], input=stdin, capture_output=True, env=full_env, timeout=30)
    return p.returncode, p.stdout, p.stderr


def run_at(script_path, args=()):
    p = subprocess.run([PY, script_path, *args], capture_output=True, timeout=30)
    return p.returncode, p.stdout, p.stderr


def hook(vault, payload, rules="true", env=None):
    stdin = json.dumps(payload).encode("utf-8") if isinstance(payload, dict) else payload
    code, out, err = run("vault_resume.py", ["--vault", vault, "--rules", rules], stdin, env)
    check(code == 0, f"hook exit code 0 (got {code}, stderr {err[:200]!r})")
    if not out.strip():
        return None
    check(all(b < 128 for b in out), "hook output is pure ASCII")
    data = json.loads(out)
    check(data["hookSpecificOutput"]["hookEventName"] == "SessionStart", "hookEventName is SessionStart")
    return data["hookSpecificOutput"]["additionalContext"]


def check(cond, label):
    print(("  ok   " if cond else "  FAIL ") + label)
    if not cond:
        FAILS.append(label)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def handoff(vault, project, session, cwd, status="in-progress", body="Next: run the tests."):
    path = os.path.join(vault, "Projects", project, "Sessions", session, "00 Handoff.md")
    write(path, f"---\ntype: handoff\ncwd: {cwd}\nstatus: {status}\nupdated: 2026-10-16 10:00\n---\n# Handoff\n\n{body}\n")
    return path


def main():
    tmp = tempfile.mkdtemp(prefix="cv-")
    try:
        vault = os.path.join(tmp, "Vault")
        work = os.path.join(tmp, "work", "app")
        os.makedirs(work)

        print("setup: create a new vault")
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--dry-run"])
        check(code == 0 and b"DRY RUN" in out and not os.path.exists(vault), "dry run writes nothing")
        code, out, _ = run("vault_setup.py", ["--vault", vault])
        check(code == 0 and b"CREATED" in out, "creates the vault")
        for rel in ("Home.md", "Projects", os.path.join("_System", "Templates", "Handoff.md"), os.path.join("_System", "Templates", "Step.md")):
            check(os.path.exists(os.path.join(vault, rel)), f"vault has {rel}")

        print("setup: adopt an existing vault without overwriting")
        write(os.path.join(vault, "Home.md"), "my own home\n")
        os.remove(os.path.join(vault, "_System", "Templates", "Step.md"))
        code, out, _ = run("vault_setup.py", ["--vault", vault])
        check(b"ADOPTED" in out, "reports adoption")
        with open(os.path.join(vault, "Home.md"), encoding="utf-8") as f:
            check(f.read() == "my own home\n", "existing Home.md kept")
        check(os.path.exists(os.path.join(vault, "_System", "Templates", "Step.md")), "missing template restored")

        print("hook: vault missing")
        ctx = hook(os.path.join(tmp, "nope"), {"source": "startup", "cwd": work})
        check(ctx is not None and "/maximuse:setup" in ctx, "points to /maximuse:setup")

        print("hook: startup, no handoff")
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check(ctx is not None and "Maximuse Vault: session notes and handoffs" in ctx, "injects the rules")
        check(vault in ctx and "{{VAULT}}" not in ctx, "rules name the vault path")
        check(len(ctx) < 3000, f"rules stay short ({len(ctx)} chars)")
        check(hook(vault, {"source": "startup", "cwd": work}, rules="false") is None, "rules off and no handoff: no output")

        print("hook: matching handoff")
        write(os.path.join(vault, "Projects", "app", "Brief.md"), "# Brief\nGoal: ship the app. Caf\u00e9 \u2713\n")
        hpath = handoff(vault, "app", "2026-10-16 login fix", work, body="Next: run `pytest -k login`. \u00e9\u2713")
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check("unfinished handoff" in ctx and "app / 2026-10-16 login fix" in ctx, "startup: pointer only")
        check("pytest -k login" not in ctx, "startup: handoff body not injected")
        for source in ("clear", "compact"):
            ctx = hook(vault, {"source": source, "cwd": work})
            check("pytest -k login" in ctx and "Goal: ship the app" in ctx, f"{source}: Brief and Handoff injected")
            check("\u2713" in ctx, f"{source}: non-ASCII text survives the ASCII JSON round trip")
        ctx = hook(vault, {"source": "clear", "cwd": work + os.sep})
        check(ctx is not None and "pytest -k login" in ctx, "trailing slash on cwd still matches")
        if os.name == "nt":
            ctx = hook(vault, {"source": "clear", "cwd": work.upper().replace("\\", "/")})
            check(ctx is not None and "pytest -k login" in ctx, "Windows: case and slash differences still match")
        ctx = hook(vault, {"source": "clear", "cwd": os.path.join(tmp, "other")})
        check("pytest -k login" not in ctx, "other folder: handoff not injected")

        print("hook: reload mark from /maximuse:save (desktop clear arrives as startup)")
        marks = os.path.join(vault, "_System", "reload-pending.json")
        code, out, _ = run("vault_find.py", ["--vault", vault, work, "--mark-reload"])
        check(code == 0 and b"RELOAD MARKED" in out and os.path.isfile(marks), "finder writes the mark")
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check("pytest -k login" in ctx and "Goal: ship the app" in ctx, "marked startup: Brief and Handoff injected")
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check("pytest -k login" not in ctx and "unfinished handoff" in ctx, "mark is used once: next startup is a pointer")
        run("vault_find.py", ["--vault", vault, work, "--mark-reload"])
        hook(vault, {"source": "clear", "cwd": work})
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check("pytest -k login" not in ctx, "a clear also takes the mark")
        run("vault_find.py", ["--vault", vault, os.path.join(tmp, "other"), "--mark-reload"])
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check("pytest -k login" not in ctx, "another folder's mark doesn't reload this one")
        write(marks, json.dumps({"c:/old/folder": 1000, "bad": "x"}))
        hook(vault, {"source": "startup", "cwd": work})
        with open(marks, encoding="utf-8") as f:
            check(json.load(f) == {}, "stale and malformed marks are pruned")
        write(marks, "not json")
        ctx = hook(vault, {"source": "startup", "cwd": work})
        check(ctx is not None and "unfinished handoff" in ctx, "broken mark file: falls back to the pointer")
        os.remove(marks)

        print("hook: size budget")
        handoff(vault, "app", "2026-10-16 login fix", work, body="x" * 30000)
        write(os.path.join(vault, "Projects", "app", "Brief.md"), "# Brief\n" + "b" * 8000)
        ctx = hook(vault, {"source": "clear", "cwd": work})
        check(len(ctx) <= 9500, f"context stays under Claude Code's 10,000-char inline limit ({len(ctx)} chars)")
        check("[truncated; read the full note at" in ctx, "truncation names the full note")
        check(ctx.rstrip().endswith("00 Handoff.md]"), "handoff is cut by the budget, not by the hard limit")
        check("Brief.md" in ctx, "Brief still has at least a pointer")

        print("hook: done handoff")
        handoff(vault, "app", "2026-10-16 login fix", work, status="done")
        ctx = hook(vault, {"source": "clear", "cwd": work})
        check("Resuming from" not in ctx and "unfinished" not in ctx, "done handoff is not reloaded")

        print("hook: config fallbacks and bad input")
        handoff(vault, "app", "2026-10-16 login fix", work)
        ctx = hook("${user_config.vault_path}", {"source": "clear", "cwd": work}, env={"CLAUDE_VAULT": vault})
        check(ctx is not None and "Resuming from" in ctx, "unsubstituted placeholder falls back to CLAUDE_VAULT")
        ctx = hook("", {"source": "clear", "cwd": work}, env={"CLAUDE_PLUGIN_OPTION_VAULT_PATH": vault})
        check(ctx is not None and "Resuming from" in ctx, "empty --vault falls back to CLAUDE_PLUGIN_OPTION_VAULT_PATH")
        check(hook(vault, b"not json", rules="false") is None, "invalid stdin: exits 0 quietly")

        print("finder")
        handoff(vault, "General", "2026-10-15 vault setup", "C:\\Users\\someone\\Desktop")
        code, out, _ = run("vault_find.py", ["--vault", vault, work, "--name", "vault", "setup"])
        text = out.decode("utf-8", "replace")
        check(code == 0 and "NAME 'vault setup': 1 match(es)" in text, "finds a handoff by part of its name")
        check("MATCH (this folder):" in text and "app / 2026-10-16 login fix" in text, "reports this folder's handoff")
        check("TEMPLATES:" in text, "prints the templates folder")
        code, out, _ = run("vault_find.py", ["--vault", vault, os.path.join(tmp, "elsewhere")])
        text = out.decode("utf-8", "replace")
        check("MATCH: none" in text and "RECENT UNFINISHED (2)" in text, "no name: lists unfinished handoffs")
        code, out, _ = run("vault_find.py", ["--vault", os.path.join(tmp, "nope"), work])
        check(b"VAULT MISSING" in out, "missing vault is reported")

        print("setup: named handoff")
        shop = os.path.join(tmp, "work", "shop")
        os.makedirs(shop)
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--handoff", "Checkout redesign", "--cwd", shop, "--dry-run"])
        named = os.path.join(vault, "Projects", "shop", "Sessions", "Checkout redesign", "00 Handoff.md")
        check(code == 0 and b"WOULD CREATE: shop / Checkout redesign" in out and not os.path.exists(named), "dry run names the handoff, writes nothing")
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--handoff", "Checkout redesign", "--cwd", shop])
        check(code == 0 and b"HANDOFF CREATED: shop / Checkout redesign" in out and os.path.isfile(named), "creates the handoff under exactly the given name")
        with open(named, encoding="utf-8") as f:
            text = f.read()
        check(f"cwd: {shop}\n" in text and "# Handoff: Checkout redesign" in text and "{{" not in text, "handoff has cwd, title, no placeholders")
        for note in ("Brief.md", "Decisions.md", "Gotchas.md"):
            check(os.path.isfile(os.path.join(vault, "Projects", "shop", note)), f"new project gets {note}")
        with open(os.path.join(vault, "Home.md"), encoding="utf-8") as f:
            check("[[Projects/shop/Brief|shop]]" in f.read(), "new project linked in Home.md")
        before = os.path.getmtime(named)
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--handoff", "checkout REDESIGN", "--cwd", work])
        check(b"HANDOFF EXISTS: shop / Checkout redesign" in out and os.path.getmtime(named) == before, "existing name (any case): reported, left alone")
        ctx = hook(vault, {"source": "startup", "cwd": shop})
        check("shop / Checkout redesign" in ctx, "hook finds the new handoff by its cwd")
        code, out, _ = run("vault_find.py", ["--vault", vault, work, "--name", "Checkout", "redesign"])
        text = out.decode("utf-8", "replace")
        check("exact: yes" in text, "finder marks an exact name")
        code, out, _ = run("vault_find.py", ["--vault", vault, work, "--name", "Checkout"])
        check(b"exact: yes" not in out and b"1 match(es)" in out, "partial name: match without the exact mark")
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--handoff", 'Fix: a/b "quotes"?', "--cwd", shop])
        check(os.path.isfile(os.path.join(vault, "Projects", "shop", "Sessions", "Fix a b quotes", "00 Handoff.md")), "characters Windows forbids are dropped")
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--handoff", "Notes", "--cwd", os.path.expanduser("~")])
        check(b"HANDOFF CREATED: General / Notes" in out, "home folder goes to the General project")
        code, out, _ = run("vault_setup.py", ["--vault", vault, "--handoff", "???", "--cwd", shop])
        check(b"HANDOFF NAME EMPTY" in out, "a name with nothing usable is refused")

        print("universal install (Codex / AGENTS.md)")
        uhome, codex, skills, repo = (os.path.join(tmp, "u", n) for n in ("maximuse", "codex", "skills", "repo"))
        write(os.path.join(codex, "AGENTS.md"), "# My own rules\nKeep this.\n")
        os.makedirs(repo)
        uvault = os.path.join(tmp, "U Vault")
        base = [PY, INSTALL, "--home", uhome, "--codex-home", codex, "--skills-dir", skills]
        p = subprocess.run(base + ["--vault", uvault, "--project", repo, "--dry-run"], capture_output=True, timeout=60)
        check(p.returncode == 0 and b"WOULD WRITE" in p.stdout and not os.path.exists(uhome) and not os.path.exists(uvault), "dry run writes nothing")
        p = subprocess.run(base + ["--vault", uvault, "--project", repo], capture_output=True, timeout=60)
        check(p.returncode == 0 and os.path.isfile(os.path.join(uvault, "Home.md")), "install creates the vault")
        for rel in ("scripts/vault_find.py", "scripts/vault_setup.py", "templates/_System/Templates/Handoff.md", "skills/maximuse-save/SKILL.md"):
            check(os.path.isfile(os.path.join(uhome, rel)), f"home has {rel}")
        with open(os.path.join(skills, "maximuse-save", "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        check(text.startswith("---\nname: maximuse-save\n") and "{{" not in text and uvault in text, "Codex skill has frontmatter and filled-in paths")
        with open(os.path.join(codex, "AGENTS.md"), encoding="utf-8") as f:
            text = f.read()
        check(text.startswith("# My own rules\nKeep this.\n") and text.count("maximuse:start") == 1 and uvault in text, "rules appended, user's AGENTS.md kept")
        check(os.path.isfile(os.path.join(repo, "AGENTS.md")), "--project gets an AGENTS.md")
        subprocess.run(base + ["--vault", uvault], capture_output=True, timeout=60)
        with open(os.path.join(codex, "AGENTS.md"), encoding="utf-8") as f:
            check(f.read().count("maximuse:start") == 1, "reinstall replaces the block, doesn't add a second")
        code, out, _ = run_at(os.path.join(uhome, "scripts", "vault_setup.py"), ["--vault", uvault, "--handoff", "Codex test", "--cwd", repo])
        check(b"HANDOFF CREATED: repo / Codex test" in out, "installed scripts start a named handoff")
        p = subprocess.run(base + ["--uninstall", "--project", repo], capture_output=True, timeout=60)
        with open(os.path.join(codex, "AGENTS.md"), encoding="utf-8") as f:
            check(f.read() == "# My own rules\nKeep this.\n", "uninstall restores the user's AGENTS.md")
        check(not os.path.exists(uhome) and not os.path.exists(os.path.join(skills, "maximuse-save")), "uninstall removes home and skills")
        check(not os.path.exists(os.path.join(repo, "AGENTS.md")), "an AGENTS.md that held only the rules is removed")
        check(os.path.isfile(os.path.join(uvault, "Home.md")), "uninstall keeps the vault")

        print("usage summary")
        cfg = os.path.join(tmp, "cfg")
        write(os.path.join(cfg, "projects", "p", "s.jsonl"), json.dumps({
            "timestamp": "2026-10-16T10:00:00Z", "requestId": "r1",
            "message": {"id": "m1", "model": "test", "usage": {"input_tokens": 10, "cache_read_input_tokens": 900, "cache_creation_input_tokens": 50, "output_tokens": 40}},
        }) + "\n")
        code, out, _ = run("usage_sum.py", env={"CLAUDE_CONFIG_DIR": cfg})
        check(code == 0 and b"cache_read" in out and b"calls=1" in out, "reads transcripts from CLAUDE_CONFIG_DIR")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print(f"{len(FAILS)} failure(s)" if FAILS else "all checks passed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
