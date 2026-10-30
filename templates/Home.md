# Maximuse Vault

One vault for every Claude conversation. Claude writes notes here as it works, so a fresh chat can pick up where the last one stopped without losing quality.

## How it works
- Each project gets a folder in `Projects/` with a **Brief**, **Decisions** and **Gotchas** note.
- Each working session gets a folder in `Projects/<Project>/Sessions/` with a **00 Handoff** note and numbered step notes. Start with `/maximuse:setup <what you want done>`: Claude names the handoff (and the desktop chat) from the task and gets to work.
- When the context gets large (~250k tokens) or you're about to step away, run `/maximuse:save`, which updates that handoff. Claude writes the notes, rebuilds the handoff and clears the chat (or asks you to type `/clear` in the terminal; not `/compact`). A hook loads the Brief and Handoff into the fresh chat automatically, and Claude checks the real state before continuing.
- In any other chat, `/maximuse:resume <the old chat's title>` picks a handoff up; on its own it lists unfinished ones by number.
- Claude's rules come from the Maximuse Vault plugin (`rules/vault-rules.md`). Templates are in `_System/Templates/`; edit them here to change what new notes look like.

## Your part
- Keep each **Brief** accurate. It's the one note that's never summarized, so put your preferences there.
- If Claude gets something wrong after a reset, check that session's handoff. A missing "Don't retry" or "Key values" entry is usually the cause.

## Projects
