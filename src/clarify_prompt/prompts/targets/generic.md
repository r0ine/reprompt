## Target profile: generic

The rewritten prompt will be used with an unspecified language model.

- Use portable Markdown headings and plain lists.
- Prefer this section order when relevant: `Goal`, `Context`, `Scope`, `Requirements`,
  `Deliverables`, `Acceptance criteria`, `Output format`.
- Avoid vendor-specific tags, tool names, hidden context assumptions, and proprietary
  features.
- Assume the target starts with no conversation history and cannot access local files,
  browse, execute code, or call tools unless the user said otherwise.
- Mark environmental assumptions explicitly.
- End with a concise language and output-format instruction.

Only rewrite the request. Do not perform it.
