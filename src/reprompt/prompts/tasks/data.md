## Task profile: data

Shape the rewritten prompt around inputs, transformations, validation, and reproducibility.

- Capture source format, schema, field semantics, volume, freshness, missing-value rules,
  units, identifiers, and expected output when known.
- Require profiling before irreversible cleaning or transformation.
- Preserve raw data and define lineage for derived artifacts.
- Make joins, filters, aggregations, outlier handling, leakage prevention, and train/test
  boundaries explicit where relevant.
- Require deterministic steps, seed control, and environment details for reproducible
  analysis.
- Ask for validation totals, rejected-row reporting, statistical assumptions, and sanity
  checks instead of accepting a chart or metric at face value.
- Keep personal or secret data minimized and avoid printing sensitive rows in logs or
  examples.
