## Task profile: review

Shape the rewritten prompt as an evidence-based inspection, not an implementation request.

- Define the artifact, review scope, relevant standards, and the severity threshold.
- Require findings to cite exact files, lines, sections, or observable behavior when that
  context is available.
- Prioritize correctness, security, data loss, compatibility, and operational risk before
  style preferences.
- For each actionable finding, require impact, triggering conditions, and a concrete repair
  direction.
- Separate blockers from improvements and omit praise or summary filler that does not help a
  decision.
- Do not authorize edits, commits, deployments, or external messages unless the user also
  asked for them.
- The output format should make “no actionable findings” a valid result.
