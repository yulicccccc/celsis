# Data Entry Workflow

## Operator loop

```text
1. Run batch Bookmarklet
2. Open next test page
3. Click Test Record field
4. Return to PowerShell
5. Press Enter
6. Wait for field sequence to complete
7. Verify values
8. Paste clipboard Note
9. Save manually
10. Repeat
```

## First-sample acceptance gate

Before continuing the batch, confirm:

- correct ETX page,
- correct record,
- correct method,
- correct start/end date,
- correct ATP,
- correct TSB,
- correct FTM,
- correct downstream yes/no/status selections,
- correct note,
- no field displacement.

If the first record is wrong, stop the batch and debug before continuing.

## Why Enter-only

Earlier interaction required typing words such as:

- `YES`
- `NEXT`

This added friction but did not materially improve control.

The retained safety gates are:

- operator chooses/open correct sample,
- operator focuses Test Record,
- one explicit Enter starts entry,
- operator verifies before Save,
- Save remains manual.

## Stop mechanism

`Q` stops the PowerShell sequence.

## Resume behavior

Batch-specific scripts may omit already completed samples.

A future generic runner should support an explicit resume/start index while preventing accidental duplicate entry.
