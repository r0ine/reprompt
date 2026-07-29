## Target profile: Claude Code

The rewritten prompt will be pasted into Claude Code (Anthropic's terminal coding assistant). Optimize for Claude's conventions:

- Use XML tags for structured sections: `<task>`, `<context>`, `<constraints>`, `<files>`, `<acceptance>`.
- Ask for explicit file paths when the request involves modifying code. Do not let Claude guess which repo or which file — request the path, or ask the user to provide it.
- Frame acceptance criteria in terms of runnable checks: `mvn package succeeds`, `pytest passes`, `npm run build has no errors`, `page renders in browser without console errors`.
- Prefer stating hypotheses over asking clarification questions when possible. Example: "I will assume the project uses JDK 21 unless you say otherwise." — this lets Claude proceed instead of stalling.
- If the request mentions the environment, honor the user's known stack (JDK 21 + Maven, Node 24, Python 3.14, RTX 4060 8GB VRAM, Windows 11). Include this in `<context>` only if it is actually relevant to the task.
- End with an explicit `<output_format>` block: what artifacts Claude should return (diff, full file, explanation-first, etc.).

Do not answer the user's request. Only rewrite it into the Claude-optimized structure above.
