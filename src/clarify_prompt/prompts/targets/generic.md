## Target profile: generic

The rewritten prompt will be pasted into an unspecified LLM. Optimize for portability:

- Use plain-text sections with clear headings — no vendor-specific tags (no XML, no proprietary syntax).
- Sections in order: `Goal`, `Context`, `Constraints`, `Acceptance criteria`, `Output format`.
- Keep the language neutral; assume the target LLM has no memory of prior turns.
- If any assumption is being made about the environment, name it explicitly ("Assuming Python 3.12 unless specified otherwise.").
- End with a one-line "Reply in the same language as this prompt." instruction — most models honor it.

Do not answer the user's request. Only rewrite it into the generic structure above.
