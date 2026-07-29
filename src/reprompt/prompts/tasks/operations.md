## Task profile: operations

Shape the rewritten prompt for deployment, infrastructure, automation, or incident work.

- Capture environment, topology, access boundaries, service dependencies, current state,
  desired state, maintenance window, and recovery requirements.
- Require read-only inspection and backups before destructive or irreversible actions.
- Separate preparation, execution, verification, rollback, and post-change monitoring.
- Make idempotency, retries, timeouts, rate limits, concurrency, secret handling, and audit
  logging explicit where relevant.
- For incidents, prioritize containment and evidence preservation before cleanup.
- Require exact commands only after targets are resolved; forbid broad deletion or
  production mutation based on guessed paths.
- Acceptance should include service health, data integrity, observability, and a tested
  rollback path proportional to risk.
