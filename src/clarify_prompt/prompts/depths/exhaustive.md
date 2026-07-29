## Detail level: exhaustive

Produce a decision-complete specification for complex work while staying within the target
model's usable context.

- Decompose the request into ordered workstreams and identify dependencies between them.
- Cover primary flow, failure paths, edge cases, security, privacy, accessibility,
  performance, compatibility, observability, migration, rollback, and documentation only
  where each concern applies.
- State assumptions, exclusions, invariants, decision points, and unresolved questions.
- Define every requested artifact and the evidence needed to accept it.
- Require the downstream model to inspect before changing, implement fully, verify, repair
  failures, and report the final state.
- Distinguish facts from inference and requirements from recommendations.
- Remove any section that would be generic filler for this particular request.
- Do not attempt to reach a token or byte quota. Completeness is measured by decision
  coverage and verifiability.
