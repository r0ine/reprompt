## Target profile: claude-code

The rewritten prompt will be executed by an agent working in a code repository.

- Use XML sections where they make boundaries clearer: `<task>`, `<context>`, `<scope>`,
  `<constraints>`, `<verification>`, and `<output_format>`.
- Treat mentioned files and repository instructions as authoritative. Tell the agent to
  inspect nearby code and project guidance before editing.
- State whether the request authorizes diagnosis, implementation, tests, dependency
  changes, commits, or deployment. Do not infer materially broader authorization.
- Prefer safe progress with explicit low-risk assumptions over unnecessary questions.
- For changes, require complete implementation, proportionate verification, and repair of
  failures before handoff.
- Preserve user work in a dirty tree and avoid destructive version-control commands unless
  explicitly requested.
- Ask the final response to lead with the outcome and cite changed files and checks.

Only rewrite the request. Do not perform it.
