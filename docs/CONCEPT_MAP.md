# Concept Map

```mermaid
flowchart TD
    A[Daily Control] --> B{Batch / date / instrument match?}
    C[Workload / reruns] --> B
    B -- No --> X[HARD STOP]
    B -- Yes --> D[Source parsing]

    D --> E[ATP from Daily Control]
    D --> F[Control blocks]
    D --> G[Sample replicate rows]

    F --> H[MF / DI group assignment]
    F --> I[TSB/FTM controls + cutoffs]

    G --> J{Any CV >= 30%?}
    J -- Yes --> K[Invalid run/media<br/>find valid rerun]
    J -- No --> L[Valid replicate set]
    K --> L

    L --> M[Max TSB RLU result column]
    L --> N[Max FTM RLU result column]

    E --> O[Batch payload]
    H --> O
    I --> O
    M --> O
    N --> O

    O --> P[Human review]
    P --> Q[Bookmarklet V3]
    Q --> R[Correct EagleTrax test page]
    R --> S[Enter-only PowerShell]
    S --> T[Human field verification]
    T --> U[Paste traceable Note]
    U --> V[Human Save]

    O --> W[Future independent Reviewer]
    W --> Y[Compare source-derived expected vs saved LIMS]
```

## Separation of responsibility

```text
AI / parser        → understand source + exceptions
Rules engine       → deterministic selection
Bookmarklet        → navigation only
PowerShell         → field prefill only
Human operator     → verify + Save
Reviewer           → independent compare + sign
```
