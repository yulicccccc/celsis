# Celsis Business Rules

## Daily Control

Use the Daily Control that matches the workload context.

Relevant checks:

- Instrument blank should remain a valid negative control per report.
- Reagent blank should remain a valid negative control per report.
- ATP Positive Control must be the Daily Control ATP row.
- The ATP **RLU** result is the value entered, not RLU1/RLU2.

## Workload controls

Each applicable media/method block supplies:

- negative control result,
- negative cutoff,
- method context,
- sample rows.

Do not assume all samples in one workload share the same block.

## CV

Threshold:

```text
CV >= 30% → invalid for automatic use
```

The invalidity belongs to the specific source run/media evidence.

Do not permanently blacklist an ETX if a valid rerun exists.

## Max RLU

For each sample and media:

```text
Max RLU = max(valid replicate rows' RLU column)
```

Wrong:

```text
max(RLU1, RLU2, RLU)
```

Correct:

```text
max(RLU result column only)
```

## Reruns

Maintain lineage at media level.

Example:

```text
Run A:
  TSB invalid CV
  FTM valid

Run B:
  TSB valid rerun

Final:
  TSB ← Run B
  FTM ← Run A
```

Do not erase Run A merely because one media failed.

## Record traceability

When multiple records contribute:

```text
Record = RUN-A, RUN-B
```

Notes should identify which control evidence came from which run where necessary.

## ETX suffixes

Examples from instrument reports may include fraction or replicate suffixes.

For EagleTrax lookup, normalize to:

```text
ETX-######-####
```

Keep the original raw label in audit/source lineage.

## Notes

Single-run standard pattern:

```text
Day 7 Sterility Read: Negative. Incubation ended on DDMonYY

RECORD: TSB -ve control = X TSB cut off = Y FTM -ve control = A FTM cut off = B
```

For cross-run cases, use explicit run-prefixed lines.

## Status dimensions

Do not collapse all state into one overloaded status.

Recommended structure:

```json
{
  "executionStatus": "...",
  "dataStatus": "...",
  "sourceStatus": "...",
  "runStatus": "...",
  "findings": []
}
```

`MATCH` means no discrepancy detected. It is not approval.
