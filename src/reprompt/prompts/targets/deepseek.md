## Target profile: deepseek

The rewritten prompt will be used with DeepSeek for technical reasoning or implementation.

- State the problem, constraints, interfaces, and expected result before background detail.
- For algorithms, include input bounds, complexity targets, numerical limits, and edge cases
  only when known.
- For code, request complete idiomatic output compatible with the supplied toolchain.
- Ask for a concise rationale or decision summary, not hidden chain-of-thought.
- Require explicit handling of uncertainty and forbid fabricated APIs, benchmarks, or
  citations.
- Separate the final artifact from verification notes so the answer remains easy to use.
- Prefer deterministic acceptance examples over broad quality adjectives.

Only rewrite the request. Do not perform it.
