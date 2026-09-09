# Evidence Index — Celsis Audit & Automation Runs

> **System Status**: `Prototype — Not validated for GxP use.`

---

## 1. Golden Case #1 Log: Batch `073126-2222`

- **Date Executed**: 2026-07-31
- **Source Scripts Verified**:
  - `Celsis_073126_2222_DataEntry.ps1` (Full 10-sample verification playlist)
  - `Celsis_073126_2222_DataEntry_Resume_EnterOnly.ps1` (9-sample resume playlist)
  - `Celsis_073126_2222_Navigator_Resume.js` (Bookmarklet / console probe navigator)

### 3-Way Forensic Audit Verification Output

```text
=== 3-WAY FORENSIC AUDIT COMPARISON REPORT ===
Batch: 073126-2222
Instrument: Advance 2
Status: Prototype — Not validated for GxP use.

[Daily Controls]
ATP Anchor:          Expected = 96305 | ChatGPT = 96305 | Antigravity = 96305  [MATCH]
TSB Control:         Expected = 992   | ChatGPT = 992   | Antigravity = 992    [MATCH]
FTM Control:         Expected = 2138  | ChatGPT = 2138  | Antigravity = 2138   [MATCH]

[Sample Verification]
1. ETX-260723-0438:  TSB=391, FTM=736  | Expected == ChatGPT == Antigravity [MATCH]
2. ETX-260723-0414:  TSB=348, FTM=667  | Expected == ChatGPT == Antigravity [MATCH]
3. ETX-260723-0401:  TSB=403, FTM=808  | Expected == ChatGPT == Antigravity [MATCH]
4. ETX-260723-0491:  TSB=413, FTM=862  | Expected == ChatGPT == Antigravity [MATCH]
5. ETX-260723-0419:  TSB=436, FTM=687  | Expected == ChatGPT == Antigravity [MATCH]
6. ETX-260723-0238:  TSB=431, FTM=733  | Expected == ChatGPT == Antigravity [MATCH]
7. ETX-260723-0471:  TSB=406, FTM=804  | Expected == ChatGPT == Antigravity [MATCH]
8. ETX-260723-0452:  TSB=399, FTM=755  | Expected == ChatGPT == Antigravity [MATCH]
9. ETX-260721-0762:  TSB=389, FTM=790  | Expected == ChatGPT == Antigravity [MATCH] (Source: ETX-260721-0762-4/5)
10. ETX-260723-0407: TSB=319, FTM=571  | Expected == ChatGPT == Antigravity [MATCH]

Score: 100/100
Issues Found & Fixed: None (Zero discrepancies)
Remaining Risks: Raw PDF file for 073126-2222 must be archived alongside this log for full audit trail.
```

---

## 2. Golden Case #2 Log: Batch `073126-2011`

- **Date Executed**: 2026-07-31
- **Source Scripts Verified**:
  - `Celsis_073126_2011_DataEntry.ps1` (Enter-Only mode)

### 3-Way Forensic Audit Verification Output

```text
=== 3-WAY FORENSIC AUDIT COMPARISON REPORT ===
Batch: 073126-2011
Instrument: Advance 2
Status: Prototype — Not validated for GxP use.

[Daily Controls]
ATP Anchor:          Expected = 112570 | Antigravity = 112570  [MATCH]
TSB Control:         Expected = 1033   | Antigravity = 1033    [MATCH]
FTM Control:         Expected = 2450   | Antigravity = 2450    [MATCH]

[Sample Verification (8 Unique Samples, All CV < 30%)]
1. ETX-260723-0424:  TSB=499, FTM=1069 | Expected == Antigravity [MATCH]
2. ETX-260723-0412:  TSB=449, FTM=855  | Expected == Antigravity [MATCH]
3. ETX-260723-0442:  TSB=336, FTM=800  | Expected == Antigravity [MATCH]
4. ETX-260723-0512:  TSB=415, FTM=903  | Expected == Antigravity [MATCH]
5. ETX-260723-0540:  TSB=372, FTM=930  | Expected == Antigravity [MATCH]
6. ETX-260723-0382:  TSB=616, FTM=970  | Expected == Antigravity [MATCH]
7. ETX-260723-0434:  TSB=452, FTM=770  | Expected == Antigravity [MATCH]
8. ETX-260723-0282:  TSB=409, FTM=887  | Expected == Antigravity [MATCH]

Score: 100/100
Issues Found & Fixed: None (Zero discrepancies)
Remaining Risks: Raw PDF files for 073126-2011 must be archived alongside log.
```

---

## 3. Golden Case #3 Log: Batch `090426-2011`

- **Date Executed**: 2026-09-04
- **Source Files**: `D:\1d.pdf` (Daily Control), `D:\1.pdf` (Batch Workload)
- **Source Scripts Verified**:
  - `Celsis_090426_2011_DataEntry_EnterOnly.ps1` (Enter-Only mode)

### 3-Way Forensic Audit Verification Output

```text
=== 3-WAY FORENSIC AUDIT COMPARISON REPORT ===
Batch: 090426-2011
Instrument: Advance 2 (ID: 2011)
Status: Prototype — Not validated for GxP use.

[Daily Controls (1d.pdf)]
ATP Anchor:          Expected = 88987 | Antigravity = 88987  [MATCH]
Reagent Blank:       Expected = 100   | Antigravity = 100    [MATCH] (<= 300)
Instrument Blank:    Expected = 31    | Antigravity = 31     [MATCH] (<= 100)

[Batch Controls (1.pdf)]
GS TSB Control:      Expected = 2176  | Antigravity = 2176   [MATCH] (Cut-off: 6526.5)
GS FTM Control:      Expected = 7334  | Antigravity = 7334   [MATCH] (Cut-off: 22002.0)
ES TSB Control:      Expected = 2597  | Antigravity = 2597   [MATCH] (Cut-off: 7791.0)
ES FTM Control:      Expected = 8089  | Antigravity = 8089   [MATCH] (Cut-off: 24267.0)

[Sample Verification (8 Unique Samples, All CV < 30%, 100% Negative)]
1. ETX-260825-0380:  TSB=2612, FTM=6383 (GS, 5 reps, Max CV=6%)  | Expected == Antigravity [MATCH]
2. ETX-260826-0689:  TSB=2306, FTM=5561 (GS, 5 reps, Max CV=12%) | Expected == Antigravity [MATCH]
3. ETX-260826-0371:  TSB=790,  FTM=2117 (GS, 2 reps, Max CV=7%)  | Expected == Antigravity [MATCH]
4. ETX-260826-0382:  TSB=2649, FTM=6761 (GS, 5 reps, Max CV=9%)  | Expected == Antigravity [MATCH]
5. ETX-260827-0684:  TSB=2953, FTM=5241 (GS, 6 reps, Max CV=8%)  | Expected == Antigravity [MATCH]
6. ETX-260826-0368:  TSB=954,  FTM=2198 (ES, 4 reps, Max CV=8%)  | Expected == Antigravity [MATCH]
7. ETX-260826-0485:  TSB=986,  FTM=3634 (ES, 5 reps, Max CV=17%) | Expected == Antigravity [MATCH]
8. ETX-260826-0374:  TSB=983,  FTM=2870 (ES, 4 reps, Max CV=10%) | Expected == Antigravity [MATCH]

Score: 100/100
Issues Found & Fixed: Fixed filename typo (081226 -> 090426) in Documents directory.
Remaining Risks: Raw PDF files (D:\1d.pdf, D:\1.pdf) must be archived alongside log.
```

---

## 4. Evidence Artifact References

- `PRD.md`: [PRD.md](file:///c:/Users/qchen/OneDrive%20-%20Professional%20Compounding%20Centers%20of%20America,%20Inc/Documents/Celsis/PRD.md)
- `PROJECT_STATE.md`: [PROJECT_STATE.md](file:///c:/Users/qchen/OneDrive%20-%20Professional%20Compounding%20Centers%20of%20America,%20Inc/Documents/Celsis/PROJECT_STATE.md)
- `ACCEPTANCE_TESTS.md`: [ACCEPTANCE_TESTS.md](file:///c:/Users/qchen/OneDrive%20-%20Professional%20Compounding%20Centers%20of%20America,%20Inc/Documents/Celsis/ACCEPTANCE_TESTS.md)
- `EVIDENCE_INDEX.md`: [EVIDENCE_INDEX.md](file:///c:/Users/qchen/OneDrive%20-%20Professional%20Compounding%20Centers%20of%20America,%20Inc/Documents/Celsis/EVIDENCE_INDEX.md)
- `Celsis_073126_2011_DataEntry.ps1`: [Celsis_073126_2011_DataEntry.ps1](file:///c:/Users/qchen/OneDrive%20-%20Professional%20Compounding%20Centers%20of%20America,%20Inc/Documents/Celsis/Celsis_073126_2011_DataEntry.ps1)
- `Celsis_090426_2011_DataEntry_EnterOnly.ps1`: [Celsis_090426_2011_DataEntry_EnterOnly.ps1](file:///c:/Users/qchen/OneDrive%20-%20Professional%20Compounding%20Centers%20of%20America,%20Inc/Documents/Celsis/Celsis_090426_2011_DataEntry_EnterOnly.ps1)

