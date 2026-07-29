## Task profile: legal-compliance

Shape the rewritten prompt as a compliance-aware document drafting brief, not legal advice.

- Capture jurisdiction, applicable regulatory framework (GDPR, KVKK, CCPA, sector-specific
  rules), and the document type (policy, terms, notice, internal procedure) explicitly.
- Require the downstream model to state its output is a draft requiring review by
  qualified counsel before use, and to flag where it made an assumption instead of citing
  a rule it cannot verify.
- Preserve mandatory disclosures, retention periods, and user rights language the user
  already supplied instead of paraphrasing them away.
- Make data categories, processing purposes, legal basis, and third-party sharing explicit
  when the document concerns personal data.
- Require version and effective-date tracking, and a plain-language summary alongside
  formal clauses when the document faces end users.
- Flag any request that would ask the model to represent unverified claims as legally
  established fact, or to draft around a disclosure requirement.
- Acceptance should include a checklist of the regulatory points addressed, an explicit
  reviewed-by-counsel gate before publication, and confirmation the draft does not
  contradict other current company policy documents when those are supplied.
