## Target profile: ChatGPT

The rewritten prompt will be pasted into ChatGPT (OpenAI, either web or GPT-4 tier). Optimize for ChatGPT's conventions:

- Use Markdown headings (`## Goal`, `## Context`, `## Constraints`, `## Acceptance criteria`, `## Output format`).
- Where useful, add a short persona line at the top (e.g. "Act as a senior backend engineer."). Only add a persona when it clearly changes the answer.
- For coding requests, name the language and version explicitly (e.g. Python 3.12, TypeScript 5.5). ChatGPT hallucinates versions without this.
- Provide 1–2 few-shot examples when the task is generative and the expected shape is not obvious.
- Structure acceptance criteria as a numbered list.
- End with `## Output format` — bullet points describing what the answer should contain (code block only? explanation first? JSON with schema X?).

Do not answer the user's request. Only rewrite it into the ChatGPT-optimized structure above.
