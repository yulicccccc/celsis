# Changelog

## 2026-09-10 — V1.0.0 Celsis End-to-End Audit & Paced Approval System Accepted

### Milestone Achievements
- **Full Batch Verification**: Complete 39-page master batch (`09SEP26.pdf`) containing 54 unique samples processed across dual instruments (`#2011`, `#2222`) and dual media (`TSB`, `FTM`).
- **Paced Approval Engine**: GxP-compliant auto-approval cadence (1~2 min natural jitter) with automatic taskbar minimization and non-blocking `[Enter]` skip / `[Q]` exit interactive controls.
- **Rule 2 Instrument Authority**: Locked rule establishing Charles River report printed `CV Pct` as the single source of truth for variation; prohibited external sample standard deviation ($ddof=1$) recalculations.
- **Rule 9 Volume Exclusivity**: Successfully intercepted 2 live pre-approval data placement anomalies (Membrane Filtration with volume mistakenly placed in Direct Inoculation column) on `ETX-260831-0737` and `ETX-260901-0557`, preventing premature uncompliant approval.
- **Rule 11 Data Review Gate**: Strictly gated approvals to samples in `Data Review`, ensuring zero premature approvals for samples still under `Sample Analysis`.
- **Fast Direct Routing**: Validated direct URL resolution via `/Submission/Details/{sid}` achieving sub-second lookup without stale DOM collisions.

## 2026-08-13 — Data Entry V1 accepted

### Accepted workflow

- JavaScript Bookmarklet + PowerShell two-script workflow.
- Bookmarklet downloader HTML established as the preferred install method.
- PowerShell changed from typing `YES` / `NEXT` to Enter-only interaction.
- Human Save remains mandatory.
- Notes copied automatically to clipboard.

### Bookmarklet V1 → V3 lessons

1. **Initial bookmark downloader failure**
   - Cause: `javascript:` code embedded in HTML `href` without correct HTML escaping.
   - Symptom: clicking bookmark appeared to do nothing.
   - Fix: HTML-escape bookmarklet URL; provide Test Bookmark.

2. **Visual contrast issue**
   - Cause: dark green row highlighting + EagleTrax dark-blue links.
   - Fix:
     - pending = light blue,
     - next = light yellow,
     - opened = light green,
     - force links to high-contrast dark blue.

3. **Intermittent ETX detection**
   - Cause: one-shot DOM scan was too brittle for asynchronous table loading / layout variation.
   - V3:
     - repeated scan,
     - whitespace / zero-width normalization,
     - row and anchor search,
     - same-origin iframe attempt,
     - semantic test-link fallback,
     - Re-scan button.

### Data entry script lessons

- One manual trigger per sample is enough.
- `YES` / `NEXT` increased friction without meaningful safety value.
- First-sample verification + manual Save are the real controls.
- Mixed MF/DI batches require per-sample method and group-specific note.

## Earlier prototype history

- Rules specification and fail-closed test scaffolding created.
- Local synthetic security tests passed.
- Repository scope mistake was identified when Git was initialized too high in the directory tree; repository isolation became a locked requirement.
- A format-preserving redactor replaced an overclaimed “desensitizer”.
- Production EagleTrax scraper connection remains deferred pending validation.
