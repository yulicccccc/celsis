# Acceptance Tests

## A. Source matching

### A1 — Correct match
Given matching Daily Control and Workload:
- proceed to extraction.

### A2 — Wrong Daily Control
Given a Daily Control from a different date/instrument:
- hard stop,
- do not generate executable entry values as if matched.

## B. ATP

- Extract Daily Control `ATP Positive Control` `RLU`.
- Do not substitute Workload positive cutoff.

## C. Max RLU

Given:

```text
RLU1  RLU2  RLU
1200  1400  1300
1500  1000  1250
```

Expected Max RLU:

```text
1300
```

Not 1500.

## D. CV

Any replicate `CV >= 30%`:
- flag invalid run/media,
- do not silently enter it.

## E. Rerun

Valid media from different runs must preserve both source records.

## F. Bookmarklet

- correctly HTML-escaped downloader,
- Test Bookmark executes,
- pending/next/opened colors readable,
- retry scan,
- Re-scan,
- unresolved list visible,
- opens correct Celsis test detail link.

## G. PowerShell

- one Enter trigger,
- correct field order,
- group-specific note,
- `Q` stops,
- no Save/Submit.

## H. First-sample gate

Before batch continuation, operator verifies all populated fields.

## I. Mixed MF/DI

A mixed batch must set each sample's method correctly and copy the corresponding note.
