# Architecture

## V1

```text
                  ┌───────────────────┐
                  │ Daily Control PDF │
                  └─────────┬─────────┘
                            │
                  ┌─────────▼─────────┐
                  │ Workload / reruns │
                  └─────────┬─────────┘
                            │
                  ┌─────────▼─────────┐
                  │ Parse + audit     │
                  │ rules / AI assist │
                  └─────────┬─────────┘
                            │
                  ┌─────────▼─────────┐
                  │ Batch payload     │
                  └──────┬───────┬────┘
                         │       │
              ┌──────────▼─┐   ┌─▼─────────────┐
              │ Bookmarklet│   │ PowerShell    │
              │ navigation │   │ field prefill │
              └──────┬─────┘   └──────┬────────┘
                     │                │
                     └───────┬────────┘
                             ▼
                     Human verification
                             ▼
                       Manual Save
```

## Target architecture

Move toward a stable structured payload:

```json
{
  "batch": {},
  "controls": [],
  "samples": [],
  "exceptions": [],
  "notes": []
}
```

Then keep executors fixed:

```text
Batch JSON
 ├─→ Bookmarklet
 ├─→ PowerShell/DOM Entry
 └─→ Reviewer
```

## Dual-lane parsing

### Deterministic lane

Stable report formats should use deterministic parsing and rules.

### AI exception lane

AI is reserved for:

- unfamiliar format,
- OCR ambiguity,
- rerun reconstruction,
- data-quality investigation.

AI should not become an invisible unversioned rules engine.
