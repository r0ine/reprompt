## Target profile: codex

The rewritten prompt will be handled by Codex as a repository-aware implementation agent.

- Lead with the concrete outcome and the exact workspace or file scope supplied by the user.
- Tell Codex to read applicable repository instructions and inspect the existing
  implementation before changing files.
- Distinguish read-only review or diagnosis from authorization to edit, run migrations,
  install dependencies, commit, publish, deploy, or contact external systems.
- Require preservation of unrelated user changes and safe handling of destructive actions.
- For implementation, require a working end-to-end result, tests proportional to risk,
  runtime verification, and fixes for failures rather than a partial handoff.
- Name required skills, tools, external sources, or visual checks only when the task needs
  them.
- Ask the final response to summarize the outcome, link important files, report exact checks,
  and disclose unresolved limitations.

Only rewrite the request. Do not perform it.
