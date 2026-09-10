import json
import re
from collections import defaultdict
import pandas as pd

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Instrument ATP anchors
DAILY_ATP = {
    "2222": 92047, # Page 3
    "2011": 95167  # Page 22
}

# Regex for ETX
# Pattern: ETX[- ]?\d{6}[- ]?\d{4} with potential container suffix
ETX_REGEX = re.compile(r"ETX[- ]?(\d{6})[- ]?(\d{4})(?:[- ]\(?(\d{1,2})|\/5)?", re.IGNORECASE)

records = []

for p in pages:
    pnum = p["page_num"]
    wl = p["wl_name"]
    batch = p["batch"]
    inst = "2222" if "2222" in wl else ("2011" if "2011" in wl else "UNKNOWN")
    
    # Check page cutoff
    cutoff = None
    media = "UNKNOWN"
    
    # First scan rows for cutoff and control
    for r in p["rows"]:
        txt = r["raw_text"]
        c_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", txt, re.I)
        if c_m:
            cutoff = float(c_m.group(1))
        
        if "tsb" in txt.lower():
            media = "TSB"
        elif "ftm" in txt.lower():
            media = "FTM"
            
    for r in p["rows"]:
        txt = r["raw_text"]
        
        # Check if control row
        if any(k in txt.lower() for k in ["control", "cal ok"]):
            continue
        if "inst" in txt.lower() or "reag" in txt.lower() or "atp" in txt.lower():
            continue
            
        # Try to find ETX
        # Normalization of known OCR glitches like ETX26... or ETX-200902 -> ETX-260902
        txt_norm = re.sub(r"ETX-?200902", "ETX-260902", txt)
        txt_norm = re.sub(r"ETX-?2008", "ETX-2608", txt_norm)
        txt_norm = re.sub(r"ETX-?2009", "ETX-2609", txt_norm)
        txt_norm = re.sub(r"ETX-?260001", "ETX-260901", txt_norm)
        txt_norm = re.sub(r"ETX-?260887", "ETX-260831", txt_norm)
        txt_norm = re.sub(r"ETX-?260890", "ETX-260830", txt_norm)
        txt_norm = re.sub(r"ETX(\d{6})", r"ETX-\1", txt_norm)
        
        m = re.search(r"ETX[- ]?(\d{6})[- ]?(\d{4})(?:[- /(]+(\d{1,2}))?", txt_norm, re.IGNORECASE)
        if not m:
            continue
            
        date_part = m.group(1)
        seq_part = m.group(2)
        container = m.group(3) if m.group(3) else "1"
        clean_etx = f"ETX-{date_part}-{seq_part}"
        
        # Now extract numbers from the line
        # Line structure: Pos | ETX... | RLU1 | RLU2 | RLU | Result | Date | Time | CV | Bkgnd
        # Let's split by '|'
        parts = [p.strip() for p in txt.split("|") if p.strip()]
        
        # Let's find numbers in the line
        # Numbers can be extracted by regex
        # Typical numbers: RLU1 (~1000-15000), RLU2 (~1000-15000), RLU (~1000-15000), CV (0-30), Bkgnd (2-10)
        nums = re.findall(r"\b\d+\b", txt)
        
        # Extract Result
        res_str = "Negative"
        if "Positive" in txt:
            res_str = "Positive"
            
        # Parse tokens
        # Let's record raw and parsed tokens
        records.append({
            "page": pnum,
            "wl": wl,
            "batch": batch,
            "inst": inst,
            "media": media,
            "cutoff": cutoff,
            "etx": clean_etx,
            "container": container,
            "raw_text": txt,
            "result": res_str,
            "nums": nums
        })

print(f"Total sample records extracted: {len(records)}")
# Group by ETX
by_etx = defaultdict(list)
for rec in records:
    by_etx[rec["etx"]].append(rec)

print(f"Unique ETX count: {len(by_etx)}")
for etx, recs in sorted(by_etx.items()):
    tsb_recs = [r for r in recs if r["media"] == "TSB"]
    ftm_recs = [r for r in recs if r["media"] == "FTM"]
    inst = recs[0]["inst"]
    print(f"{etx} ({inst}): TSB={len(tsb_recs)} recs, FTM={len(ftm_recs)} recs | Pages: {sorted(list(set(r['page'] for r in recs)))}")
