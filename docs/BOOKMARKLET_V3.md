# Bookmarklet V3

## Purpose

The Bookmarklet is a navigation assistant only.

It should:

- identify target ETX rows,
- make targets visually obvious,
- open the correct Celsis test detail page one at a time.

It should not:

- fill EagleTrax fields,
- click Save,
- submit forms,
- approve records.

## Why V3 exists

### Failure 1 — broken bookmark installer

A generated downloader embedded raw JavaScript inside an HTML `href`.

Quotes in the JavaScript broke/truncated the link.

**Fix:** HTML-escape the complete `javascript:` URL.

A Test Bookmark is useful for distinguishing:

- browser/bookmark installation problems,
- from ETX matching problems.

### Failure 2 — poor contrast

Dark-green table rows made native dark-blue links difficult to read.

**Accepted palette:**

- pending → `#e0f2fe` light blue,
- next → `#fff3bf` light yellow,
- opened → `#dcfce7` light green,
- link text → dark blue.

### Failure 3 — intermittent missing IDs

A one-shot `document.querySelectorAll('tr')` scan can run before the table has fully rendered.

V3 adds:

- repeated scans,
- small delay between scans,
- `Re-scan page`,
- normalized matching,
- multiple link-selection strategies.

## Matching logic

Normalize text:

- trim,
- collapse whitespace,
- ignore case,
- remove zero-width characters.

Find ETX using:

1. table row text,
2. anchor text,
3. other accessible row context,
4. same-origin iframe document if available.

## Link-selection priority

1. URL matches `/SubmissionTest/Details/`
2. link text contains `Celsis Sterility Test`
3. href contains `SubmissionTest`
4. historical index fallback

## Missing interpretation

A missing ETX after retries does not automatically mean code failure.

Possible causes:

- ETX not present under current filter,
- pagination,
- Rows/Page setting,
- date/status/test-type filters,
- delayed rendering,
- different page,
- real DOM change.

The UI should report unresolved IDs explicitly.
