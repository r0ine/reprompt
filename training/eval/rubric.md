# Judge rubric

Evaluate the rewritten prompt on a 1–5 scale.

1. **Clarity** — is the intent unambiguous? Could a stranger act on it without questions?
2. **Structure** — are goal, context, acceptance criteria, and output format present?
3. **Faithfulness** — does the rewritten prompt preserve the user's original intent? No scope creep, no missing detail.
4. **Actionability** — could the target LLM take action immediately, or would it still need clarification?
5. **Concision** — does the rewrite avoid unnecessary preamble, filler, or repetition?

Scoring:
- **5** — excellent, no meaningful defect.
- **4** — good, minor stylistic issue only.
- **3** — acceptable, one section thin but usable.
- **2** — poor, missing a required section or misrepresents the intent.
- **1** — broken, unreadable, off-topic, or fabricated content.

Return a JSON object: `{"score": int, "rationale": "..."}`. Rationale ≤ 40 words.
