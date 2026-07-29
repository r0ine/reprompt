## Task profile: coding

Shape the rewritten prompt as an implementation brief.

- Identify the requested behavior, affected surface, existing constraints, and public
  contracts that must remain stable.
- Instruct the downstream model to inspect repository conventions and nearby code before
  editing.
- Name supplied files, symbols, versions, commands, schemas, and interfaces exactly.
- Require complete implementation rather than snippets when the user asks for a working
  change.
- Cover validation, failure behavior, backward compatibility, security, and performance
  only where the change touches them.
- Acceptance should include the closest relevant tests, type checks, lint, build, and a
  direct runtime or browser check when available.
- Ask the final answer to list changed files, verification evidence, and remaining
  limitations without dumping unrelated implementation detail.
