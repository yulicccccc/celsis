import json

with open("celsis_110926_database.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# 1. Remove phantom ETX-260903-0306
db = [s for s in db if s["Sample"] != "ETX-260903-0306"]

# 2. Update verified fields
for s in db:
    sid = s["Sample"]
    if sid == "ETX-260902-0511":
        s["Max TSB RLU"] = 2693
        s["Max FTM RLU"] = 7651
        s["Max CV%"] = "2%"
        s["Pages"] = [17, 18]
        s["Status"] = "PASS"
        s["Notes"] = "100% Valid Negative (Page 17 TSB=2693, Page 18 row 3 FTM=7651)"
    elif sid == "ETX-260902-0631":
        s["Max CV%"] = "27%"
        s["Status"] = "PASS"
        s["Notes"] = "100% Valid Negative (Page 22 row 2 printed CV Pct: 27%)"
    elif sid == "ETX-260903-0079":
        s["Max CV%"] = "9%"
        s["Status"] = "PASS"
        s["Notes"] = "100% Valid Negative (Page 11 row 6 printed CV Pct: 9%)"
    elif sid == "ETX-260903-0088":
        s["Max CV%"] = "6%"
        s["Status"] = "PASS"
        s["Notes"] = "100% Valid Negative (Page 11 row 14 printed CV Pct: 6%)"
    elif sid == "ETX-260903-0386":
        s["Max TSB RLU"] = 196
        s["Max FTM RLU"] = 295
        s["Max CV%"] = "7%"
        s["Status"] = "PASS"
        s["Notes"] = "100% Valid Negative (Page 10 row 5 printed CV Pct: 7%)"
    elif sid == "ETX-260903-0789":
        s["Max CV%"] = "9%"
        s["Status"] = "PASS"
        s["Notes"] = "100% Valid Negative (Page 10 row 10 printed CV Pct: 9%)"

db.sort(key=lambda x: x["Sample"])

with open("celsis_110926_database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2)

print("=" * 75)
print(f"Final 11SEP26 Database: {len(db)} unique samples")
pass_cnt = sum(1 for s in db if s["Status"] == "PASS")
block_cnt = sum(1 for s in db if "BLOCK" in s["Status"])
print(f"  • PASS:     {pass_cnt} / {len(db)}")
print(f"  • BLOCK:    {block_cnt} / {len(db)}")
print("=" * 75)

for s in db:
    print(f"  {s['Sample']} | Inst: #{s['Instrument']} | ATP: {s['Daily ATP']} | TSB: {str(s['Max TSB RLU']):<6} | FTM: {str(s['Max FTM RLU']):<6} | CV%: {s['Max CV%']:<4} | Status: {s['Status']}")
