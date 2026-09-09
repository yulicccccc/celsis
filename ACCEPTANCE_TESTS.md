# Acceptance Test Suite — Celsis LIMS Automation

> **Current System Status**: `Prototype — Not validated for GxP use.`

---

## 1. Acceptance Criteria Protocol

A batch payload is deemed **PASSED** if and only if:
```text
Human Manual Expected == ChatGPT Output == Antigravity Python Output
```
1. **Daily Control Match**: `ATP Positive Control`, `TSB Control`, and `FTM Control` values match 100%.
2. **Sample Count Match**: Number of valid samples extracted matches expected sample count.
3. **ID & Suffix Handling**: Suffixes (e.g., `-4/5`) are correctly stripped for LIMS page lookup without breaking sample identity.
4. **Max RLU Match**: `TSB` and `FTM` Max RLU values match human-verified expected values for every sample.
5. **CV Failsafe**: Any replicate with `CV >= 30%` or `Positive` result is blocked from the whitelist.
6. **No Phantom Predictions**: Zero unverified predictions or missing field errors.

---

## 2. Golden Case #1: `073126-2222` Test Specification

### 2.1 Metadata
- **Batch Record**: `073126-2222`
- **Instrument**: Advance 2
- **Date Range**: 07/24/2026 – 07/31/2026
- **Truth Anchors**:
  - `ATP Positive Control`: `96305`
  - `TSB Negative Control`: `992`
  - `FTM Negative Control`: `2138`

### 2.2 Expected Sample Matrix (10 Samples)

| # | Sample ID | Raw Source ID | Method | ATP | TSB Max RLU | FTM Max RLU | Result Status |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :--- |
| 1 | `ETX-260723-0438` | `ETX-260723-0438` | `d` | 96305 | 391 | 736 | Pass |
| 2 | `ETX-260723-0414` | `ETX-260723-0414` | `d` | 96305 | 348 | 667 | Pass |
| 3 | `ETX-260723-0401` | `ETX-260723-0401` | `d` | 96305 | 403 | 808 | Pass |
| 4 | `ETX-260723-0491` | `ETX-260723-0491` | `d` | 96305 | 413 | 862 | Pass |
| 5 | `ETX-260723-0419` | `ETX-260723-0419` | `d` | 96305 | 436 | 687 | Pass |
| 6 | `ETX-260723-0238` | `ETX-260723-0238` | `d` | 96305 | 431 | 733 | Pass |
| 7 | `ETX-260723-0471` | `ETX-260723-0471` | `d` | 96305 | 406 | 804 | Pass |
| 8 | `ETX-260723-0452` | `ETX-260723-0452` | `d` | 96305 | 399 | 755 | Pass |
| 9 | `ETX-260721-0762` | `ETX-260721-0762-4/5` | `d` | 96305 | 389 | 790 | Pass (Suffix Cleaned) |
| 10 | `ETX-260723-0407` | `ETX-260723-0407` | `d` | 96305 | 319 | 571 | Pass |

---

## 3. Comparison Matrix & Score Card

| Verification Field | Manual Expected | ChatGPT Output | Antigravity Python Output | Match Result |
| :--- | :--- | :--- | :--- | :--- |
| **ATP Truth Anchor** | `96305` | `96305` | `96305` | ✅ 100% Match |
| **TSB Control** | `992` | `992` | `992` | ✅ 100% Match |
| **FTM Control** | `2138` | `2138` | `2138` | ✅ 100% Match |
| **Sample Count** | `10` | `10` | `10` | ✅ 100% Match |
| **Special Suffix `0762-4/5`** | `ETX-260721-0762` | `ETX-260721-0762` | `ETX-260721-0762` | ✅ 100% Match |
| **TSB RLU Values (All 10)** | Exact values | Exact values | Exact values | ✅ 100% Match |
| **FTM RLU Values (All 10)** | Exact values | Exact values | Exact values | ✅ 100% Match |

**Overall Result**: **PASS (100% Consistent)**

---

## 4. Golden Case #3: `090426-2011` Test Specification

### 4.1 Metadata
- **Batch Record**: `090426-2011`
- **Instrument**: Advance 2 (ID: 2011)
- **Date Range**: 08/28/2026 – 09/04/2026 (Incubation ended 04Sep26)
- **Truth Anchors (Daily Control - 1d.pdf)**:
  - `ATP Positive Control`: `88987` (RLU1=89891, RLU2=88082, CV=1%, Bkgnd=4)
  - `Reagent Blank`: `100` (<= 300)
  - `Instrument Blank`: `31` (<= 100)
- **Batch Negative Controls (1.pdf)**:
  - **Group GS (Batches A & B)**:
    - `TSB,DI,-ve control-GS`: `2176` (Negative Cut-off: `6526.5`)
    - `FTM,DI,-ve control-GS`: `7334` (Negative Cut-off: `22002.0`)
  - **Group ES (Batches C & D)**:
    - `TSB,DI,-ve control-ES`: `2597` (Negative Cut-off: `7791.0`)
    - `FTM,DI,-ve control-ES`: `8089` (Negative Cut-off: `24267.0`)

### 4.2 Expected Sample Matrix (8 Samples)

| # | Sample ID | Raw Source Replicates | Group | Method | ATP | TSB Max RLU | FTM Max RLU | Max CV | Result Status |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| 1 | `ETX-260825-0380` | 5 bottles ((1) to (5)) | GS | `d` | 88987 | 2612 | 6383 | 6% | Pass (100% Negative) |
| 2 | `ETX-260826-0689` | 5 bottles ((1) to (5)) | GS | `d` | 88987 | 2306 | 5561 | 12% | Pass (100% Negative) |
| 3 | `ETX-260826-0371` | 2 bottles ((1) to (2)) | GS | `d` | 88987 | 790 | 2117 | 7% | Pass (100% Negative) |
| 4 | `ETX-260826-0382` | 5 bottles ((1) to (5)) | GS | `d` | 88987 | 2649 | 6761 | 9% | Pass (100% Negative) |
| 5 | `ETX-260827-0684` | 6 bottles ((1) to (6)) | GS | `d` | 88987 | 2953 | 5241 | 8% | Pass (100% Negative) |
| 6 | `ETX-260826-0368` | 4 bottles ((1) to (4)) | ES | `d` | 88987 | 954 | 2198 | 8% | Pass (100% Negative) |
| 7 | `ETX-260826-0485` | 5 bottles ((1) to (5)) | ES | `d` | 88987 | 986 | 3634 | 17% | Pass (100% Negative) |
| 8 | `ETX-260826-0374` | 4 bottles ((1) to (4)) | ES | `d` | 88987 | 983 | 2870 | 10% | Pass (100% Negative) |

### 4.3 Comparison Matrix & Score Card (`090426-2011`)

| Verification Field | Manual Expected | Script Output | Antigravity Python Output | Match Result |
| :--- | :--- | :--- | :--- | :--- |
| **ATP Truth Anchor** | `88987` | `88987` | `88987` | ✅ 100% Match |
| **GS TSB Control** | `2176` | `2176` | `2176` | ✅ 100% Match |
| **GS FTM Control** | `7334` | `7334` | `7334` | ✅ 100% Match |
| **ES TSB Control** | `2597` | `2597` | `2597` | ✅ 100% Match |
| **ES FTM Control** | `8089` | `8089` | `8089` | ✅ 100% Match |
| **Sample Count** | `8` | `8` | `8` | ✅ 100% Match |
| **TSB RLU Values (All 8)** | Exact values | Exact values | Exact values | ✅ 100% Match |
| **FTM RLU Values (All 8)** | Exact values | Exact values | Exact values | ✅ 100% Match |
| **CV Failsafe (<30%)** | Max 17% | Max 17% | Max 17% | ✅ 100% Pass |

**Overall Result**: **PASS (100% Consistent)**

