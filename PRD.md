# Product Requirements Document (PRD) — Celsis-to-LIMS Automation & Audit System

> **System Status**: `Prototype — Not validated for GxP use.`
> **Current Focus**: Offline Golden Case Validation & Deterministic Architecture.

---

## 1. System Vision & Boundaries

### 1.1 Objective
Automate the forensic audit, data extraction, and payload formatting of Celsis Rapid Microbiology (USP 71) assay reports for entry into the LIMS / EagleTrax laboratory information system.

### 1.2 Dual-Track Architecture
```text
                    Raw Celsis PDF / Text Input
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
   AI Exception Lane                         Deterministic App Lane
   (Unstructured / Exception Batches)        (Standard Batch Validation)
          │                                         │
 OCR/Multi-Run/Anomaly                       Deterministic Parser & Rules
 Human Explanation & Audit                   Strict JSON Payload Generation
          │                                         │
          └───────────── Batch JSON ────────────────┘
                           │
                  Human Review & Approval
                           │
            Universal Bookmarklet + PowerShell Macro
                            │
                    Manual Save & Sign
```

### 1.3 Mandatory 4-in-1 Delivery Package
Whenever generating Celsis data entry automation deliverables, the agent MUST deliver the complete 4-in-1 suite:
1. **① 书签下载器 HTML (`<BATCH>_书签下载器.html`)**: Standalone page with one-click drag-and-drop JavaScript bookmarklet to locate & open test pages in EagleTrax.
2. **② Enter-only PowerShell (`<BATCH>_DataEntry_EnterOnly.ps1`)**: Keystroke automation macro with automated clipboard note management.
3. **③ RLU 核对表 (`<BATCH>_Review_Table.tsv`)**: Tab-separated comparison dataset.
4. **④ 完整包 ZIP (`<BATCH>_Complete_Package.zip`)**: Bundled zip containing all deliverables above.


---

## 2. Locked Business & Audit Rules

### Rule 1: Truth Anchor Verification (ATP Control)
- **Extraction**: Extract `ATP Positive Control` value from Daily Control.
- **Enforcement**: Must be mapped globally to all sample payload records.
- **Failsafe**: If Daily Control is missing or mismatched, flag immediate error.

### Rule 2: 30% CV Failsafe (Physical Block)
- **Condition**: Scan all replicate readings. If any replicate `CV >= 30%` or Result is `Positive`, trigger an absolute physical exclusion.
- **Action**: Remove the bottle from the entry whitelist and output a re-run action item (`.ics`). Do NOT auto-populate failing samples.

### Rule 3: Max RLU Extraction & OCR Decoupling
- **Flattening**: For valid samples, flatten replicate readings.
- **Max Extraction**: Extract highest `RLU` for TSB and highest `RLU` for FTM.
- **OCR Remediation**: Decouple concatenated OCR numbers (e.g. `35583582` -> `RLU1=3606, RLU2=3582` -> `RLU=3582`).

### Rule 4: Suffix Cleaning & ID Normalization
- **Special Suffixes**: Strip batch iteration suffixes (e.g. `ETX-260721-0762-4/5` -> `ETX-260721-0762`) for EagleTrax ID matching, while preserving source traceability in logs.

### Rule 5: Traceable LIMS Test Notes & Record Suture
- **Cross-Run Suture**: If a sample spans multiple runs, format Record ID as a comma-separated list (e.g., `040926-2011-2, 040926-2011-3`).
- **Absolute Note Prefixing**: Cut-off parameters in LIMS Notes must use absolute batch prefixes (e.g. `040926-2011-2: TSB -ve control = ...`), avoiding relative terms like "Run 2".

### Rule 6: Deterministic Link Resolution Protocol (MS Check Strategy)
- **Target Search Endpoint**: `https://etrax.eagleanalytical.com/Submission`
- **Dynamic Link Discovery Sequence**:
  1. **Clear Filters**: Trigger `#ClearButton` to purge cached search state.
  2. **Exact ETX Search**: Populate `#srchCriteria` with normalized ETX ID and dispatch `#FindButton`.
  3. **Tab Navigation**: Navigate to the `Tests` tab (`a[href='#SubmissionTests']`).
  4. **Strict DOM Synchronization (Race-Condition Guard)**: Explicitly await until the table row specifically containing the queried ETX ID is rendered (`table tbody tr:has-text('<ETX>')`), preventing stale AJAX row collisions from preceding samples.
  5. **Test Disambiguation**: Scan matching rows for `Celsis Sterility Test` (case-insensitive) and extract the authentic `/SubmissionTest/Details/<ID>` URL.
- **Traceability**: All resolved URLs must be recorded into `celsis_<BATCH>_links_verified.json` before initiating field auditing or approval execution.

### Rule 7: Modifications Field Audit Rule (Note-to-Field Synchronization)
- **DOM Anchor**: `Modification (Optional)` (`SubmissionTestResults_2__Value`)
- **Note-to-Field Rule**:
  - Scan sample Test Notes and Prep Notes (`SubmissionTestNoteList`).
  - If the notes explicitly state `No Modifications` or contain **NO mention of formulation or procedural modifications**, the `Modification (Optional)` field MUST strictly be **`N/A`**.
  - If leaving blank or containing unverified values, flag an immediate **Audit Discrepancy (Red Flag)**.
  - If notes specify a legitimate modification (e.g. customized rinse volume, neutralizer), the field must precisely reflect that documented modification.

### Rule 8: GxP-Compliant Paced Auto-Approval Cadence (3~5 Minutes Per Sample)
- **Background & Intent**: In regulated laboratory environments (GxP / EagleTrax LIMS), instant sub-second bulk approvals produce unnatural audit trails that raise compliance flags during quality reviews. Automated approvals must replicate the natural cadence of a diligent QA reviewer.
- **Cadence Specification**:
  - Minimum interval: `180 seconds` (3.0 minutes).
  - Maximum interval: `300 seconds` (5.0 minutes).
  - Pacing behavior: Randomized jitter between 180s and 300s after each successful approval to avoid mechanical fixed-frequency patterns.
- **Idempotency & Pre-check**:
  - Before initiating an approval, check current status. If already `Approved`, log and skip immediately (0 seconds wait).
  - Physical exclusion of Rule 2 failing samples (e.g. `CV >= 30%`) is strictly preserved; failing samples are NEVER touched by the approval engine.
- **Resumability**:
  - Progress is incrementally persisted to `celsis_batch_approval_progress.json` after every single sample.
  - If interrupted (user pause, network disconnection), the runner resumes without duplicate actions.

### Rule 9: Method-Volume Mutual Exclusivity Audit Rule (方法与体积栏位互斥复核法则)
- **Background**: EagleTrax has two distinct optional volume fields:
  1. `Amount of sample filtered into media (Membrane filtration only) (Optional)` (`SubmissionTestResults_3__Value`)
  2. `Amount of sample added into media (Direct Inoculation Only) (Optional)` (`SubmissionTestResults_4__Value`)
- **Strict Placement Enforcement**:
  - **When `Method Performed` == `Membrane Filtration` (MF)**:
    - The sample volume MUST be located exclusively in the **Filtered Volume** field (`SubmissionTestResults_3__Value`).
    - The **Added Volume** field (`SubmissionTestResults_4__Value`) MUST be strictly **EMPTY / BLANK**.
  - **When `Method Performed` == `Direct Inoculation` (DI)**:
    - The sample volume MUST be located exclusively in the **Added Volume** field (`SubmissionTestResults_4__Value`).
    - The **Filtered Volume** field (`SubmissionTestResults_3__Value`) MUST be strictly **EMPTY / BLANK**.
- **Audit Flag & Auto-Approval Gatekeeper**:
  - If a sample's volume is entered in the wrong method field, or entered in both fields, or missing when specified in Prep Notes, trigger an immediate **Audit Discrepancy (Volume Inversion / Placement Anomaly)** and block automated approval until reviewed by the lead analyst.


---

## 3. Human-in-the-Loop Safeguards

1. **No Automatic Save/Submit**: Automation scripts must populate input fields ONLY. Final inspection and Save/Sign actions must be performed manually by a qualified analyst.
2. **First-Sample Verification**: Analysts must visually verify the first populated record field-by-field before proceeding.
3. **No Unexplained Speculation**: All data extractions and exception flags must trace back to raw PDF evidence.

---

## 4. Current Constraints & Out-of-Scope Items

- **NO Cloudflare Pages Deployment**: Deployment is deferred until offline Golden Cases are 100% validated.
- **NO Direct EagleTrax Integration**: System does not communicate with production servers via network APIs.
