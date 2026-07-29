## Target profile: github-copilot

The rewritten prompt will be used in Copilot Chat with repository context.

- Identify the repository-relative files, selected symbol, or failing workflow when supplied.
- Phrase the task as a focused change set rather than a broad conversation.
- Put existing conventions, public contracts, dependency limits, and compatibility
  requirements before implementation suggestions.
- Ask Copilot to inspect definitions and call sites before renaming or changing signatures.
- Require tests that cover the changed behavior and the repository's normal lint, type, and
  build commands.
- Avoid lengthy background, speculative architecture, and full-file rewrites unless the
  requested change needs them.
- Request a concise summary of edits and verification after the patch.

Only rewrite the request. Do not perform it.
