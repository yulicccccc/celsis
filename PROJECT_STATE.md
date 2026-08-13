# Project State

## Current state

**Milestone:** Data Entry V1 usable  
**User acceptance:** 2026-08-13  
**Status:** Prototype — Not validated for GxP use

## What is working

### Data interpretation

- Matching Daily Control vs Workload is treated as a prerequisite.
- ATP comes from Daily Control.
- Max RLU is taken from the `RLU` result column.
- CV >= 30% is a hard exception.
- MF / DI can coexist in the same workload.
- Suffix-normalized ETX lookup is supported conceptually.
- Cross-run reconstruction rules are documented.

### Navigation

Bookmarklet V3:

- high-contrast visual states,
- retries asynchronous DOM scans,
- searches rows / anchors,
- supports same-origin iframe inspection,
- prefers SubmissionTest Details,
- has Re-scan,
- opens one page at a time.

### Data entry

PowerShell V1:

- Enter-only operator trigger,
- fixed tab sequence confirmed in current EagleTrax form,
- group-specific notes,
- clipboard support,
- `Q` stop,
- no automatic Save/Submit.

## Known limitations

1. Bookmarklet can only find rows present in the loaded/accessible DOM.
   Pagination and active filters may hide valid ETXs.
2. PowerShell uses keyboard focus and tab order.
   A UI change can displace fields.
3. Day-7 start date may be derived and requires first-sample confirmation.
4. PDF/OCR text can be malformed.
5. No formal production validation has been completed.
6. Independent Reviewer automation is not yet production-approved.

## Immediate next engineering steps

1. Convert batch-specific generated data into a structured `Batch JSON`.
2. Keep Bookmarklet and PowerShell as fixed templates reading that payload.
3. Build Golden Cases from de-identified original reports.
4. Add exact three-way checks:
   - human expected,
   - JS / web engine,
   - Python reviewer engine.
5. Add explicit source hashes and run/media lineage.
6. Replace tab-navigation with DOM-field targeting only after field IDs/names are mapped and tested.
