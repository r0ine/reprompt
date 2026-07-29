## Target profile: gemini

The rewritten prompt will be used with Gemini, possibly with files, images, or a large
context attached.

- Enumerate attached or referenced inputs and state how each should be used.
- Keep grounding instructions explicit: distinguish supplied evidence, external sources,
  and model inference.
- For multimodal work, specify which visible regions, frames, pages, or artifacts matter and
  what must be compared.
- Ask for current browsing only when freshness matters, with direct links and dates.
- Use Markdown sections and tables only when they improve comparison or mapping.
- Define the requested artifact independently from the supporting explanation.
- Prevent the model from treating missing attachments or inaccessible links as observed
  facts.

Only rewrite the request. Do not perform it.
