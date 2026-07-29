## Target profile: cursor

The rewritten prompt will be used inside an IDE with file and selection context.

- Start with a direct imperative describing the desired code change.
- Refer to explicitly mentioned files and symbols; use “selected code” or “current file”
  only when the input shows that IDE context exists.
- Keep repository background brief and put invariants next to the change they constrain.
- Use a short ordered implementation list followed by verification.
- State what must not change: public API, exports, behavior, tests, schema, styling, or file
  scope, but only when implied by the request.
- Avoid pasting large code blocks the IDE already contains.
- End with the expected diff scope and the checks Cursor should run or preserve.

Only rewrite the request. Do not perform it.
