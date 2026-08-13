# Celsis Automation

Celsis Automation is a human-in-the-loop workflow for converting Charles River Celsis / AMPiScreen sterility report data into accurate, reviewable EagleTrax data-entry payloads.

## Current milestone

**Data Entry V1 — accepted for day-to-day usability on 2026-08-13.**

The accepted V1 workflow is:

```text
Daily Control + Workload report
        ↓
AI / parser extracts & audits data
        ↓
Batch-specific high-contrast Bookmarklet
        ↓
EagleTrax target test page
        ↓
Enter-only PowerShell field entry
        ↓
Human field verification
        ↓
Paste traceable Test Note
        ↓
Human Save / sign-off
```

**Important:** This project is a prototype and workflow aid. It is **not validated for GxP use** and must not replace required SOP review, independent verification, or electronic/signature controls.

## Why this project exists

Manual Celsis data entry requires repeatedly:

- matching Daily Control and Workload files,
- finding ATP Positive Control,
- checking every replicate CV,
- selecting the correct TSB / FTM values,
- determining MF vs DI,
- handling suffixes and reruns,
- locating the correct EagleTrax test page,
- entering a long fixed sequence of fields,
- writing traceable notes,
- and avoiding silent transcription errors.

The goal is not to remove the human reviewer. The goal is to remove repetitive navigation and transcription while making exceptions more visible.

## Repository map

```text
.
├── README.md
├── PRD.md
├── PROJECT_STATE.md
├── AGENTS.md
├── CHANGELOG.md
├── .gitignore
├── docs/
│   ├── CONCEPT_MAP.md
│   ├── BUSINESS_RULES.md
│   ├── DATA_ENTRY_WORKFLOW.md
│   ├── BOOKMARKLET_V3.md
│   ├── POWERSHELL_ENTRY.md
│   ├── VALIDATION_AND_SAFETY.md
│   ├── ARCHITECTURE.md
│   ├── DECISIONS_AND_LESSONS.md
│   └── ACCEPTANCE_TESTS.md
└── templates/
    ├── batch_payload.example.json
    ├── bookmarklet_v3_template.js
    └── data_entry_enter_only_template.ps1
```

## V1 operator workflow

1. Provide the Daily Control and Workload report for the batch.
2. Confirm Daily Control and Workload match on date / instrument / record family.
3. Review extracted ATP, controls, cutoffs, methods, CV status, and Max RLU table.
4. Install the batch Bookmarklet using the generated bookmark-downloader HTML.
5. On the EagleTrax Celsis list page, click the Bookmarklet.
6. Use **Open next test page**.
7. On the opened test page, click **Test Record**.
8. Return to PowerShell and press **Enter once**.
9. Verify every populated field.
10. Paste the automatically copied Test Note.
11. Save manually.
12. Repeat.

The scripts must never automatically click Save or Submit.

## Stable UX requirements

- Bookmark installation should be via a downloadable HTML “bookmark downloader”.
- Bookmarklet row colors:
  - light blue = pending,
  - light yellow = next,
  - light green = opened.
- Links must remain high-contrast and readable.
- Bookmarklet must retry DOM scanning and provide a **Re-scan page** button.
- PowerShell should require **Enter only**, not typing `YES` / `NEXT`.
- `Q` is the stop command.
- Notes should be copied automatically to the clipboard.
- First sample must always be treated as an acceptance check.
