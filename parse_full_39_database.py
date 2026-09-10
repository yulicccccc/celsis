import json
import re
from collections import defaultdict
import pandas as pd

DAILY_ATP = {
    "2222": 92047, # Page 3
    "2011": 95167  # Page 28
}

PAGE_MEDIA = {
    6: "TSB", 7: "FTM",
    8: "TSB", 9: "FTM",
    10: "TSB", 11: "FTM",
    12: "TSB", 13: "FTM",
    14: "TSB", 15: "FTM",
    16: "TSB", 17: "FTM",
    18: "TSB", 19: "FTM",
    20: "TSB", 21: "FTM",
    22: "TSB", 23: "FTM",
    24: "TSB", 25: "FTM",
    29: "TSB", 30: "FTM",
    31: "TSB", 32: "FTM",
    33: "TSB", 34: "FTM",
    35: "TSB", 36: "FTM", 37: "FTM",
    38: "TSB", 39: "FTM"
}

with open("celsis_090926_full_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

def clean_etx(txt):
    m = re.search(r"ETX[- ]?(\d{6})[- ]?(\d{4})", txt, re.I)
    if not m:
        return None
    d1, d2 = m.group(1), m.group(2)
    if d1.startswith("20"):
        d1 = "26" + d1[2:]
    if d1 == "260001":
        d1 = "260901"
    if d1 == "260887":
        d1 = "260831"
    if d1 == "260890":
        d1 = "260830"
    if d1 == "260031":
        d1 = "260831"
    if d1 == "260801":
        d1 = "260901"
    return f"ETX-{d1}-{d2}"

sample_readings = defaultdict(lambda: {"TSB": [], "FTM": [], "CVs": [], "instruments": set(), "pages": set(), "results": []})

for p in pages:
    pnum = p["page_num"]
    wl = p["wl_name"]
    batch = p["batch"]
    inst = "2222" if "2222" in wl else ("2011" if "2011" in wl else "UNKNOWN")
    
    current_media = PAGE_MEDIA.get(pnum, "UNKNOWN")
    if current_media == "UNKNOWN":
        continue
            
    for r in p["rows"]:
        txt = r["raw_text"]
        sid = clean_etx(txt)
        if not sid:
            continue
            
        is_pos = "positive" in txt.lower()
        is_neg = "negative" in txt.lower()
        res_str = "Positive" if is_pos else ("Negative" if is_neg else "Unknown")
        
        sample_readings[sid]["instruments"].add(inst)
        sample_readings[sid]["pages"].add(pnum)
        sample_readings[sid]["results"].append(res_str)
        
        # Look for 3 numbers before negative/positive: rlu1, rlu2, rlu
        m_neg = re.search(r"(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(?:negative|positive)", txt, re.I)
        if m_neg:
            r1, r2, rlu = int(m_neg.group(1)), int(m_neg.group(2)), int(m_neg.group(3))
            mean = (r1 + r2) / 2.0
            std = abs(r1 - r2) / (2 ** 0.5)
            cv = (std / mean) * 100.0 if mean > 0 else 0.0
            sample_readings[sid]["CVs"].append(cv)
            sample_readings[sid][current_media].append(rlu)
        else:
            # Fallback: single number before negative
            m_single = re.search(r"(\d{2,6})\s*\|\s*(?:negative|positive)", txt, re.I)
            if m_single:
                rlu = int(m_single.group(1))
                sample_readings[sid][current_media].append(rlu)

print(f"Total parsed samples from PDF: {len(sample_readings)}")

# Also load existing verified readings from the first batch
with open("celsis_090926_final_audit_report.json", "r", encoding="utf-8") as f:
    old_audit = json.load(f)
old_map = {s["Sample"]: s for s in old_audit}

summary_rows = []
for sid in sorted(sample_readings.keys()):
    data = sample_readings[sid]
    inst = list(data["instruments"])[0] if data["instruments"] else "2222"
    atp = DAILY_ATP.get(inst, 92047)
    
    max_tsb = max(data["TSB"]) if data["TSB"] else "N/A"
    max_ftm = max(data["FTM"]) if data["FTM"] else "N/A"
    max_cv = max(data["CVs"]) if data["CVs"] else 0.0
    
    # If this sample was already fully verified in old_map, use old verified values
    if sid in old_map and old_map[sid].get("PDF TSB") != "N/A" and old_map[sid].get("PDF FTM") != "N/A":
        old_item = old_map[sid]
        max_tsb = old_item["PDF TSB"]
        max_ftm = old_item["PDF FTM"]
        max_cv_str = old_item["Max CV%"].replace("%", "")
        max_cv = float(max_cv_str) if max_cv_str else max_cv
        inst = old_item["Instrument"]
        atp = old_item["PDF ATP"]
        rule_status = old_item["Audit Result"]
    else:
        is_blocked = (max_cv >= 30.0) or ("Positive" in data["results"])
        rule_status = "BLOCK (CV >= 30%)" if is_blocked else "PASS"
    
    summary_rows.append({
        "Sample": sid,
        "Instrument": inst,
        "Daily ATP": atp,
        "Max TSB RLU": max_tsb,
        "Max FTM RLU": max_ftm,
        "Max CV%": f"{max_cv:.1f}%",
        "Pages": sorted(list(data["pages"])),
        "Rule 2 Status": rule_status
    })

df = pd.DataFrame(summary_rows)
df.to_json("celsis_090926_full_parsed_summary.json", orient="records", indent=2)
print("Saved celsis_090926_full_parsed_summary.json successfully!")

pass_count = sum(1 for r in summary_rows if "PASS" in r["Rule 2 Status"])
block_count = sum(1 for r in summary_rows if "BLOCK" in r["Rule 2 Status"])
print(f"Total: {len(summary_rows)} | PASS: {pass_count} | BLOCK: {block_count}")
