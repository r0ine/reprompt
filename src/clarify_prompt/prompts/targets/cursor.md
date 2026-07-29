## Target profile: Cursor

The rewritten prompt will be pasted into Cursor (IDE-integrated coding assistant). Cursor already sees open files and selection context; keep the prompt short and direct.

- Use imperative mood: "Extract...", "Rename...", "Replace...", "Preserve...".
- Refer to file/selection through IDE-relative language: "the selected function", "this component", "the imports at the top".
- Do not restate what Cursor already sees. Do not paste large code blocks — Cursor has them.
- Prefer 4–8 short numbered instructions over a long paragraph.
- End with a one-line invariant list: "Do not: touch tests / rename exports / change public API." — clear "do nots" prevent Cursor from over-editing.

Do not answer the user's request. Only rewrite it into the Cursor-optimized structure above.
