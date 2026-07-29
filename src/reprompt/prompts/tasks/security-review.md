## Task profile: security-review

Shape the rewritten prompt as a security assessment or threat-modeling brief.

- Capture the asset or system boundary under review, trust boundaries crossed, data
  sensitivity, and the attacker model (external unauthenticated, authenticated user,
  insider) relevant to the request.
- Require the downstream model to rate findings by exploitability and impact, not just
  list them, and to distinguish confirmed issues from suspected ones needing verification.
- Separate remediation (fixes the root cause) from mitigation (reduces risk without
  fixing it) and require the response to state which one it is proposing.
- Forbid producing runnable exploit code or attack payloads beyond what is needed to prove
  a finding in a controlled, authorized environment the user confirms they own or are
  contracted to test.
- Require secrets, credentials, and real user data encountered during the review to be
  redacted in the response rather than reproduced.
- For dependency or supply-chain findings, name the affected package, version, and known
  CVE identifier when one exists instead of a vague severity claim.
- Acceptance should include a severity-ranked finding list, a proposed fix or mitigation
  per finding, and confirmation that any test performed stayed within the authorized
  scope.
