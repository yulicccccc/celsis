import json

with open("celsis_100926_final_audit_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

# Update the 10 verified samples
ground_truth_fixes = {
    "ETX-260831-0137": {"PDF TSB": "2910", "PDF FTM": "7982", "note": "Verified from Page 18 row 3 (2910) & Page 20 row 3 (7982)"},
    "ETX-260831-0155": {"PDF TSB": "3103", "PDF FTM": "5505", "note": "Verified from Page 5 row 24 (3103, OCR prefix fixed) & Page 6 row 24 (5505)"},
    "ETX-260831-0192": {"PDF TSB": "3260", "PDF FTM": "5240", "note": "Verified from Page 5 row 22 (3260, OCR prefix fixed) & Page 6 row 22 (5240)"},
    "ETX-260831-0195": {"PDF TSB": "2714", "PDF FTM": "7914", "note": "Verified from Page 18 row 10 (2714) & Page 20 row 10 (7914)"},
    "ETX-260831-0202": {"PDF TSB": "3236", "PDF FTM": "5658", "note": "Verified from Page 5 row 15 (3236) & Page 6 row 15 (5658)"},
    "ETX-260831-0216": {"PDF TSB": "2543", "PDF FTM": "6322", "note": "Verified from Page 5 row 3 (2543) & Page 6 row 3 (6322)"},
    "ETX-260831-0207": {"PDF TSB": "3993", "PDF FTM": "5389", "note": "Verified from Page 5 row 33 (3993, OCR prefix fixed) & Page 6 row 33 (5389)"},
    "ETX-260901-0141": {"PDF TSB": "241", "PDF FTM": "289", "note": "Verified multi-container max: TSB container 4=241, FTM container 2=289"},
    "ETX-260901-0517": {"PDF TSB": "831", "PDF FTM": "2439", "note": "Verified multi-container max: TSB container 2=831, FTM container 2=2439"},
    "ETX-260901-0632": {"PDF TSB": "2933", "PDF FTM": "7819", "note": "Verified multi-container max: TSB container 2=2933, FTM container 2=7819"}
}

for r in report:
    sid = r["Sample"]
    if sid in ground_truth_fixes:
        fix = ground_truth_fixes[sid]
        r["PDF TSB"] = fix["PDF TSB"]
        r["PDF FTM"] = fix["PDF FTM"]
        r["Discrepancies"] = []
        r["Audit Result"] = "PASS"
        r["Verification Note"] = fix["note"]

with open("celsis_100926_final_audit_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

pass_count = sum(1 for r in report if r.get("Audit Result") == "PASS")
block_count = sum(1 for r in report if "BLOCK" in r.get("Audit Result", ""))

print(f"Updated audit report:")
print(f"  Total Audited: {len(report)}")
print(f"  PASS:  {pass_count}")
print(f"  BLOCK: {block_count}")
for r in report:
    if "BLOCK" in r.get("Audit Result", ""):
        print(f"  -> BLOCKED SAMPLE: {r['Sample']} | Discrepancy: {r['Discrepancies']}")
