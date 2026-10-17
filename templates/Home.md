# Maximuse Vault

One vault for every Claude conversation. Claude writes notes here as it works, so a fresh chat can pick up where the last one stopped without losing quality.

## How it works
- Each project gets a folder in `Projects/` with a **Brief**, **Decisions** and **Gotchas** note.
- Each working session gets a folder in `Projects/<Project>/Sessions/` with a **00 Handoff** note and numbered step notes.
- When the context gets large (~250k tokens) or you're about to step away, run `/maximuse:save`. Claude writes the notes, rebuilds the handoff and clears the chat (or asks you to type `/clear` in the terminal; not `/compact`). A hook loads the Brief and Handoff into the fresh chat automatically, and Claude checks the real state before continuing.
- In any other chat, `/maximuse:resume <part of the name>` picks a handoff up by name.
- Claude's rules come from the Maximuse Vault plugin (`rules/vault-rules.md`). Templates are in `_System/Templates/`; edit them here to change what new notes look like.

## Your part
- Keep each **Brief** accurate. It's the one note that's never summarized, so put your preferences there.
- If Claude gets something wrong after a reset, check that session's handoff. A missing "Don't retry" or "Key values" entry is usually the cause.

## Projects
