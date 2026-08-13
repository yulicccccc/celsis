# Product Requirements Document — Celsis Automation

**Status:** Data Entry V1 accepted for usability; validation work continues  
**Owner / operator:** Laboratory user  
**System context:** Charles River Celsis / AMPiScreen → EagleTrax LIMS  
**Safety posture:** Human-in-the-loop; no automatic Save / Submit  
**GxP status:** Prototype — Not validated for GxP use

---

## 1. Problem

Celsis sterility data entry is repetitive but not mechanically simple.

A single batch may require the operator to:

- connect a Daily Control report to the correct Workload report,
- extract ATP Positive Control,
- determine which control block applies to each sample,
- distinguish MF and DI methods,
- inspect all replicate CV values,
- select the maximum **RLU result column** value for TSB and FTM,
- recognize malformed / concatenated PDF text,
- preserve rerun lineage,
- normalize ETX labels for EagleTrax lookup,
- locate the correct Celsis test-detail page among many submissions,
- enter a long fixed field sequence,
- create traceable notes,
- and perform an independent review.

The risk is not only time. Repetitive navigation and transcription create opportunities for silent mismatch.

---

## 2. Product goal

Create a reliable human-in-the-loop Celsis automation system that:

1. reduces repetitive navigation and typing,
2. detects data problems before entry,
3. preserves source/run traceability,
4. separates deterministic rules from exception handling,
5. keeps final Save / sign-off under human control,
6. can later support independent reviewer automation.

---

## 3. Non-goals

V1 does **not**:

- automatically Save or Submit EagleTrax records,
- sign or approve results,
- replace SOP-required review,
- infer missing values silently,
- connect a production reviewer scraper without validation,
- claim GxP validation,
- treat an AI answer as the official source of truth.

---

## 4. V1 accepted operator experience

### 4.1 Inputs

At minimum:

- Daily Control report for the correct instrument/day.
- Workload report for the batch.
- Any rerun report needed to resolve invalid CV or missing media data.

### 4.2 Outputs

For each batch:

1. batch integrity check,
2. ATP value,
3. method/group assignments,
4. TSB / FTM controls and cutoffs,
5. per-ETX Max RLU table,
6. exception / rerun flags,
7. high-contrast JavaScript Bookmarklet downloader,
8. Enter-only PowerShell script,
9. traceable Test Note(s),
10. first-sample acceptance values.

### 4.3 Execution

```text
Bookmarklet
→ opens one exact EagleTrax test page
→ operator clicks Test Record
→ PowerShell Enter
→ fields are populated
→ Note copied
→ operator reviews
→ operator manually saves
```

---

## 5. Locked business requirements

### R-001 — Daily Control truth anchor

ATP must come from the matching **Daily Control** report, specifically the `ATP Positive Control` row's `RLU` result value.

A Workload positive cutoff is not the ATP value.

### R-002 — Source matching

Before data entry, Daily Control and Workload must be checked for the correct:

- assay date,
- instrument identifier,
- record family / batch context.

A mismatched Daily Control is a hard stop.

### R-003 — CV failsafe

If **any replicate** used for a sample/media has `CV >= 30%`, that run/media result is invalid for automatic use.

The system must:

- flag the exception,
- preserve the run lineage,
- not silently use the invalid read,
- search/accept a valid rerun only when source evidence supports it.

A sample may ultimately use TSB from one run and FTM from another if that is the documented valid lineage.

### R-004 — Max RLU rule

For valid replicates, select the maximum value from the report's **`RLU` result column**.

Do **not** take the maximum across `RLU1` or `RLU2`.

This rule applies independently to TSB and FTM.

### R-005 — Method grouping

Method is derived from the applicable control block / report context:

- `m` = MF
- `d` = DI

A mixed Workload can contain multiple independent MF / DI groups.

### R-006 — Dynamic control groups

The system must not assume a fixed number of groups.

Groups are determined by source structure, including:

- TSB / FTM control blocks,
- method,
- record/run,
- media,
- volume/additive/control context.

### R-007 — ETX normalization

Source labels may contain suffixes such as:

- `-4/5`
- `-3/5`
- replicate markers

The EagleTrax lookup typically uses the base ETX:

`ETX-YYMMDD-NNNN`

The raw source label must still be preserved in traceability.

### R-008 — Cross-run reconstruction

When a sample is completed from multiple runs:

- keep each source run,
- keep which media/value came from which run,
- use comma-separated records where required by the current LIMS convention,
- use record-prefixed note lines so the note remains understandable out of context.

### R-009 — No silent OCR repair

Concatenated or malformed text such as merged numbers must not be guessed silently.

If the underlying report image/table makes the value clear, it may be manually resolved with an explicit trace.

Otherwise mark:

`REVIEW REQUIRED`

### R-010 — Day 7 dates

The end date is the read/incubation-end date.

A start date calculated as seven calendar days earlier is a **derived value**, not a directly sourced value, unless the source explicitly contains it.

The first record must verify the date before batch continuation.

### R-011 — Human final control

Automation may prefill data.

Automation must **not** automatically:

- click Save,
- Submit,
- approve,
- sign.

The operator remains responsible for verification and final action.

---

## 6. Bookmarklet requirements

### Functional

- Find the requested ETX rows on the current EagleTrax list.
- Prefer `/SubmissionTest/Details/` links.
- Fall back to visible `Celsis Sterility Test` text.
- Fall back to a general SubmissionTest link only when necessary.
- Open only one target at a time.
- Visually mark progress.

### Robustness

The accepted V3 design must:

- normalize whitespace,
- strip zero-width characters for matching,
- search table rows and anchors,
- inspect same-origin iframes when accessible,
- retry scanning for asynchronous page loading,
- expose a manual **Re-scan page** button,
- report unresolved IDs instead of pretending success.

### Visual design

- Pending: light blue.
- Next: light yellow.
- Opened: light green.
- Text: dark gray / black.
- Links: high-contrast dark blue.

### Installation

The batch deliverable should include a “bookmark downloader” HTML page.

The `javascript:` URL must be HTML-escaped in the anchor `href`; failure to do this can truncate the bookmarklet and make it appear to do nothing.

---

## 7. PowerShell requirements

### Interaction

For each sample:

- user opens the correct page,
- user clicks `Test Record`,
- user presses **Enter once**,
- script fills the established sequence,
- note is copied to clipboard,
- user verifies and saves.

Do not require `YES` / `NEXT`.

`Q` must stop the sequence.

### Established field sequence

```text
Test Record
→ Method
→ N/A
→ TAB
→ TAB
→ ml
→ Start Date
→ End Date
→ y
→ ATP
→ TSB Max RLU
→ FTM Max RLU
→ y
→ y
→ y
→ y
→ p
```

The script stops before Save/Submit.

### Mixed groups

Each sample object must carry its own:

- method,
- TSB value,
- FTM value,
- note/group metadata.

A global note is not acceptable for a mixed-group batch.

---

## 8. Reviewer target architecture

The future independent Reviewer must not merely compare against the Entry Assistant's output.

Reviewer flow:

```text
Original source
→ independent parsing
→ directly read saved LIMS fields
→ expected vs actual comparison
→ discrepancy report
→ human reviewer decision/signature
```

Entry and Reviewer may share:

- approved rules specification,
- low-level source parsing utilities.

They must not share Entry's final selected result object as the Reviewer's source of truth.

---

## 9. Deterministic + AI dual-lane architecture

### Deterministic lane

For ordinary stable reports:

```text
Source
→ parser
→ rules engine
→ structured Batch JSON
→ human review
→ fixed Bookmarklet / PowerShell executors
```

### AI exception lane

For:

- new layouts,
- OCR/parse ambiguity,
- cross-run reconstruction,
- unusual missing data,
- new exception types.

AI may explain and propose a resolution, but source evidence and human confirmation remain required.

Long term, the daily-changing object should be **Batch JSON**, not a completely rewritten executor.

---

## 10. Success metrics

A release is better when it reduces:

- manual navigation count,
- manual keystrokes,
- time to first correctly populated sample,
- ETX lookup failures,
- transcription errors,
- unexplained parser guesses.

It must not reduce traceability or human review.

---

## 11. Acceptance criteria for Data Entry V1

- [x] Bookmarklet can locate a real batch and open correct test pages.
- [x] Bookmarklet downloader installs successfully.
- [x] High-contrast state colors are readable.
- [x] Enter-only PowerShell sequence works on the tested EagleTrax form.
- [x] Mixed method groups can carry distinct notes.
- [x] Script stops before Save.
- [x] Daily Control mismatch can be detected before entry.
- [x] User accepted V1 usability on 2026-08-13.
- [ ] Formal Golden Case suite completed.
- [ ] Production-independent Reviewer validated.
- [ ] GxP validation completed.
