---
name: usage
description: Compare Claude Code token usage (cache-read share, context per call, output, totals) with the baseline saved in the Maximuse Vault, to see whether clearing early and resuming from handoffs is paying off. Use when the user asks how their usage or token savings are going.
disable-model-invocation: true
---

# Token usage versus baseline

Run:

```
"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/scripts/usage_sum.py"
```

The baseline lives in `_System/Usage baseline.md` inside the vault `${user_config.vault_path}` (expand a leading `~` to the home folder before reading or writing it).

- **No baseline yet:** create that note with today's date and the script's `[all]` block copied word for word, and tell the user the baseline is saved and that later runs compare against it. Suggest running `/maximuse:usage` again after a week of using `/maximuse:save`.
- **Baseline exists:** compare the `[7d]` block with it: average context per call, cache-read share, output, and total. Report the change in a short table and say which habits drove it (for example, average context dropping because chats were cleared near 250k tokens).
