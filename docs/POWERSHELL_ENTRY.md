# PowerShell Entry Macro

## Role

PowerShell handles repetitive keyboard entry after the operator has already opened the correct EagleTrax test page and placed focus in the `Test Record` field.

## Accepted field sequence

```text
Record
TAB
Method
TAB
N/A
TAB
TAB
TAB
ml
TAB
Start Date
TAB
End Date
TAB
y
TAB
ATP
TAB
TSB Max RLU
TAB
FTM Max RLU
TAB
y
TAB
y
TAB
y
TAB
y
TAB
p
```

Equivalent logical form:

```text
Record
→ Method
→ N/A
→ skip two fields
→ ml
→ Start Date
→ End Date
→ y
→ ATP
→ TSB
→ FTM
→ 4 × y
→ p
```

No Save action follows.

## Per-sample payload

Each sample should carry:

```text
ID
Record
Method
ATP
TSB
FTM
Note / control group
```

This prevents mixed MF/DI batches from accidentally sharing the wrong note.

## Interaction design

Prompt:

```text
Open page, click Test Record, press Enter. Q=stop
```

Do not require typing YES or NEXT.

## Clipboard

After field entry:

- copy the sample's correct group note to clipboard,
- instruct operator to verify and paste.

## Risk

PowerShell SendKeys depends on:

- browser focus,
- current tab order,
- page response timing.

Therefore the first-sample acceptance gate is mandatory.

Long-term replacement: stable DOM selectors after a formal EagleTrax field map is obtained and validated.
