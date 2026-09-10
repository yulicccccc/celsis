import json
from collections import defaultdict
import pandas as pd

with open("parsed_containers_solved.json", "r", encoding="utf-8") as f:
    containers = json.load(f)

# Instrument Daily ATP
DAILY_ATP = {
    "2222": 92047, # Page 3
    "2011": 95167  # Page 22
}

# Group containers by ETX
by_etx = defaultdict(list)
for c in containers:
    by_etx[c["etx"]].append(c)

summary_rows = []

for etx in sorted(by_etx.keys()):
    recs = by_etx[etx]
    inst = recs[0]["inst"]
    atp = DAILY_ATP.get(inst, "N/A")
    
    tsb_recs = [r for r in recs if r["media"] == "TSB"]
    ftm_recs = [r for r in recs if r["media"] == "FTM"]
    
    # TSB metrics
    tsb_wl = ", ".join(sorted(list(set(r["wl"] for r in tsb_recs)))) if tsb_recs else "None"
    tsb_pages = ", ".join(str(p) for p in sorted(list(set(r["page"] for r in tsb_recs)))) if tsb_recs else "None"
    tsb_cutoff = tsb_recs[0]["cutoff"] if tsb_recs and tsb_recs[0]["cutoff"] else "N/A"
    
    tsb_rlus = [r["rlu"] for r in tsb_recs if r["rlu"] is not None]
    max_tsb_rlu = max(tsb_rlus) if tsb_rlus else "N/A"
    
    # FTM metrics
    ftm_wl = ", ".join(sorted(list(set(r["wl"] for r in ftm_recs)))) if ftm_recs else "None"
    ftm_pages = ", ".join(str(p) for p in sorted(list(set(r["page"] for r in ftm_recs)))) if ftm_recs else "None"
    ftm_cutoff = ftm_recs[0]["cutoff"] if ftm_recs and ftm_recs[0]["cutoff"] else "N/A"
    
    ftm_rlus = [r["rlu"] for r in ftm_recs if r["rlu"] is not None]
    max_ftm_rlu = max(ftm_rlus) if ftm_rlus else "N/A"
    
    # CV% check across all containers
    all_cvs = [r["cv"] for r in recs if r["cv"] is not None]
    max_cv = max(all_cvs) if all_cvs else 0.0
    
    # Overall Result
    # All results must be Negative
    results = [r["result"] for r in recs]
    has_positive = any(res == "Positive" for res in results)
    cv_failed = any(cv >= 30.0 for cv in all_cvs)
    
    overall_res = "Negative"
    if has_positive or cv_failed:
        overall_res = "FAIL / RERUN"
        
    containers_tested = f"TSB: {len(tsb_recs)}, FTM: {len(ftm_recs)}"
    
    summary_rows.append({
        "Sample": etx,
        "Instrument": inst,
        "ATP Positive": atp,
        "Containers": containers_tested,
        "TSB Cutoff": tsb_cutoff,
        "Max TSB RLU": max_tsb_rlu,
        "TSB Page": tsb_pages,
        "FTM Cutoff": ftm_cutoff,
        "Max FTM RLU": max_ftm_rlu,
        "FTM Page": ftm_pages,
        "Max CV%": f"{max_cv}%",
        "Result": overall_res
    })

df = pd.DataFrame(summary_rows)
print(df.to_string(index=False))

df.to_csv("celsis_090926_summary.csv", index=False)
df.to_json("celsis_090926_summary.json", orient="records", indent=2)
print("\nSaved celsis_090926_summary.csv and .json successfully!")
