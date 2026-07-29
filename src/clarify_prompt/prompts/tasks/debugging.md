## Task profile: debugging

Shape the rewritten prompt around evidence, reproduction, diagnosis, and regression safety.

- Preserve the exact symptom, error text, stack trace, environment, triggering input, and
  last-known-good behavior supplied by the user.
- Require reproduction before modification whenever the environment permits it.
- Separate observed facts, hypotheses, root cause, fix, and verification.
- Direct the downstream model to inspect logs and the narrowest relevant code path first.
- Do not authorize broad refactors unless the root cause demonstrates they are necessary.
- Require a regression test or equivalent repeatable check that fails before the fix and
  passes after it.
- Include fallback diagnostics when the issue cannot be reproduced, and forbid claiming a
  root cause without evidence.
