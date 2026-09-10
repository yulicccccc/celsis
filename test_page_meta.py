import json
import re
from collections import defaultdict

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# First, map Daily Controls to Instruments
daily_controls = {
    "2222": {
        "ATP": 92047, # Page 3: ATP Positive Control RLU=92047
        "Reagent_Blank": 75,
        "Inst_Blank": 2 # Rerun 3 on Page 5
    },
    "2011": {
        "ATP": 95167, # Page 22: ATP Positive Control RLU=95167
        "Reagent_Blank": 74,
        "Inst_Blank": 32 # Page 20
    }
}

# Workload page mappings
# Let's verify each page's media and cutoffs
page_metadata = {}
for p in pages:
    pnum = p["page_num"]
    wl = p["wl_name"]
    batch = p["batch"]
    cutoff = p.get("neg_cutoff")
    
    # Determine instrument from wl
    inst = "2222" if "2222" in wl else ("2011" if "2011" in wl else "")
    
    # Check rows for cutoff and control
    ctrl_name = None
    media = None
    for r in p["rows"]:
        txt = r["raw_text"]
        c_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", txt, re.I)
        if c_m:
            cutoff = float(c_m.group(1))
            
        if any(k in txt.lower() for k in ["control", "cal ok"]):
            ctrl_name = txt
            if "tsb" in txt.lower():
                media = "TSB"
            elif "ftm" in txt.lower():
                media = "FTM"
            elif "reagent" in txt.lower():
                media = "Reagent Blank"
            elif "inst" in txt.lower():
                media = "Inst Blank"
            elif "atp" in txt.lower():
                media = "ATP Positive"

    page_metadata[pnum] = {
        "page_num": pnum,
        "wl": wl,
        "inst": inst,
        "batch": batch,
        "cutoff": cutoff,
        "media": media,
        "ctrl_name": ctrl_name
    }

print("Page metadata overview:")
for pnum, meta in sorted(page_metadata.items()):
    if meta["media"] in ["TSB", "FTM"]:
        print(f"Page {pnum:02d}: WL={meta['wl']} | Inst={meta['inst']} | Media={meta['media']} | Cutoff={meta['cutoff']}")

