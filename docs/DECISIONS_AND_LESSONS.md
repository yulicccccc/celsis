# Decisions and Lessons

## D-001 — Two scripts are currently better than one

The workflow deliberately separates:

- JavaScript → navigation,
- PowerShell → field entry.

This keeps page discovery and keyboard entry independently debuggable.

## D-002 — Bookmarklet instead of repeated F12 paste

A bookmark is faster for daily use.

A downloader HTML is preferred because it gives a drag-to-bookmarks installation experience.

## D-003 — Human Save is retained

The project optimizes repetitive work without removing the final human control.

## D-004 — First sample is the batch acceptance test

The first record validates:

- field order,
- dates,
- values,
- note,
- browser focus behavior.

## D-005 — High-contrast colors are a functional requirement

Visual state must improve readability, not merely decorate the page.

## D-006 — One-shot DOM scanning was rejected

Real pages can render asynchronously.

V3 uses retry + Re-scan.

## D-007 — Absolute record prefixes in notes

Notes should remain interpretable when copied out of conversational context.

## D-008 — Do not overclaim parser certainty

Malformed text, new layouts, or OCR artifacts require explicit review when source evidence is insufficient.

## D-009 — Repository isolation

A previous broad `git init` accidentally scoped unrelated project files.

New rule:

> Initialize Git only inside the dedicated Celsis project root.

## D-010 — Do not track portable runtimes by default

Avoid committing portable Node executables and other opaque binaries unless there is a documented controlled distribution reason.
