import json
import pandas as pd

with open("celsis_090926_summary.json", "r", encoding="utf-8") as f:
    summary_data = json.load(f)

with open("celsis_090926_links_verified.json", "r", encoding="utf-8") as f:
    links_data = json.load(f)

links_map = {item["etx_id"]: item for item in links_data}

full_records = []
for s in summary_data:
    etx = s["Sample"]
    link_info = links_map.get(etx, {})
    url = link_info.get("url", "N/A")
    status = link_info.get("status", "N/A")
    
    rec = {
        "Sample": etx,
        "Instrument": s["Instrument"],
        "ATP Positive": s["ATP Positive"],
        "Containers": s["Containers"],
        "Max TSB RLU": s["Max TSB RLU"],
        "TSB Cutoff": s["TSB Cutoff"],
        "Max FTM RLU": s["Max FTM RLU"],
        "FTM Cutoff": s["FTM Cutoff"],
        "Max CV%": s["Max CV%"],
        "Audit Status": s["Result"],
        "LIMS Status": status,
        "EagleTrax URL": url
    }
    full_records.append(rec)

df = pd.DataFrame(full_records)
df.to_csv("celsis_090926_step2_full_verified.tsv", sep="\t", index=False)
df.to_json("celsis_090926_step2_full_verified.json", orient="records", indent=2)

print("Saved celsis_090926_step2_full_verified.tsv and .json successfully!")
