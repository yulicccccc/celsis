import json
import re
from collections import defaultdict
import pandas as pd

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

DAILY_ATP = {
    "2222": 92047, # Page 3
    "2011": 95167  # Page 22
}

def clean_ocr_line(txt):
    t = txt
    # Fix common OCR typos in ETX prefix
    t = re.sub(r"ET[FfXx][ -]*", "ETX-", t)
    t = re.sub(r"ETX-?200902", "ETX-260902", t)
    t = re.sub(r"ETX-?2008", "ETX-2608", t)
    t = re.sub(r"ETX-?2009", "ETX-2609", t)
    t = re.sub(r"ETX-?260001", "ETX-260901", t)
    t = re.sub(r"ETX-?260887", "ETX-260831", t)
    t = re.sub(r"ETX-?260890", "ETX-260830", t)
    t = re.sub(r"ETX-?260831\s*-0837", "ETX-260831-0837", t)
    t = re.sub(r"ETX-?260831-041\s*344", "ETX-260831-0413-(4", t)
    t = re.sub(r"ETX-?260831-034\s*0", "ETX-260831-0310", t)
    t = re.sub(r"ETX-?260901-0228-\(3", "ETX-260901-0229-(3", t)
    t = re.sub(r"ETX-?260901-0417-6", "ETX-260901-0411-(6", t)
    t = re.sub(r"ETX-?260901-041147", "ETX-260901-0411-(7", t)
    t = re.sub(r"ETX-?260901-0602\(4", "ETX-260901-0692-(4", t)
    return t

def parse_line_values(txt):
    # Extracts RLU1, RLU2, RLU, CV, Result
    # Usually contains: | RLU1 | RLU2 | RLU | Result | Date | Time | CV | Bkgnd
    res = "Negative"
    if "Positive" in txt:
        res = "Positive"
    elif "Cal OK" in txt:
        res = "Cal OK"
        
    # Find all sequences of digits
    # Let's clean noise characters
    cleaned = txt.replace("]", "|").replace("[", "|").replace("}", "|").replace("{", "|").replace("I", "|").replace("l", "|")
    tokens = [t.strip() for t in cleaned.split("|") if t.strip()]
    
    # Try to find the RLU block
    # RLU values are typically between 100 and 99999
    # CV is typically between 0 and 50
    # Let's extract all numbers from tokens
    # Or find tokens that match numbers
    numbers_found = []
    for tok in tokens:
        # if token has pure digits
        m = re.findall(r"\b\d+\b", tok)
        for num in m:
            # ignore dates like 9, 2026
            if num not in ["9", "2026", "2024", "2025"]:
                numbers_found.append(int(num))
                
    # In Celsis: [Pos, RLU1, RLU2, RLU, (CV), (Bkgnd)] or similar
    # If we have RLU1, RLU2, RLU:
    # Notice: RLU is usually near the average of RLU1 and RLU2!
    rlu1, rlu2, rlu, cv = None, None, None, None
    
    # Let's use regex on the raw line to find patterns: \d+\s*\|\s*\d+\s*\|\s*\d+
    triplet_m = re.search(r"(\d{2,6})\s*[\s|]+\s*(\d{2,6})\s*[\s|]+\s*(\d{2,6})", cleaned)
    if triplet_m:
        n1, n2, n3 = int(triplet_m.group(1)), int(triplet_m.group(2)), int(triplet_m.group(3))
        # If n3 is between min(n1,n2)-50 and max(n1,n2)+50, then n1=RLU1, n2=RLU2, n3=Mean RLU!
        if min(n1, n2) * 0.7 <= n3 <= max(n1, n2) * 1.3:
            rlu1, rlu2, rlu = n1, n2, n3
            
    # Try to find CV% (usually near the end before or after date/time)
    # e.g., | 1 | 2 or 1%
    cv_m = re.search(r"(\d{1,2})\s*%\s*", txt)
    if cv_m:
        cv = int(cv_m.group(1))
    elif rlu1 and rlu2 and rlu:
        # calculate CV% directly: std / mean * 100
        mean_val = (rlu1 + rlu2) / 2.0
        if mean_val > 0:
            std_val = ((rlu1 - mean_val)**2 + (rlu2 - mean_val)**2)**0.5 # sample std for n=2: abs(rlu1-rlu2) / sqrt(2)
            # Actually Celsis uses sample std: abs(rlu1 - rlu2) * 0.70710678 / mean * 100
            calc_cv = round((abs(rlu1 - rlu2) / (2**0.5)) / mean_val * 100.0, 1)
            cv = calc_cv

    return rlu1, rlu2, rlu, cv, res

parsed_containers = []

for p in pages:
    pnum = p["page_num"]
    wl = p["wl_name"]
    batch = p["batch"]
    inst = "2222" if "2222" in wl else ("2011" if "2011" in wl else "UNKNOWN")
    
    cutoff = None
    media = "UNKNOWN"
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
        raw_txt = r["raw_text"]
        txt = clean_ocr_line(raw_txt)
        
        if any(k in txt.lower() for k in ["control", "cal ok", "inst", "reag", "atp"]):
            continue
            
        m = re.search(r"ETX[- ]?(\d{6})[- ]?(\d{4})(?:[- /(]+(\d{1,2}))?", txt, re.IGNORECASE)
        if not m:
            continue
            
        clean_etx = f"ETX-{m.group(1)}-{m.group(2)}"
        container = m.group(3) if m.group(3) else "1"
        
        rlu1, rlu2, rlu, cv, res = parse_line_values(txt)
        
        parsed_containers.append({
            "page": pnum,
            "wl": wl,
            "batch": batch,
            "inst": inst,
            "media": media,
            "cutoff": cutoff,
            "etx": clean_etx,
            "container": container,
            "rlu1": rlu1,
            "rlu2": rlu2,
            "rlu": rlu,
            "cv": cv,
            "result": res,
            "raw": txt
        })

print(f"Total parsed containers: {len(parsed_containers)}")
with open("parsed_containers.json", "w", encoding="utf-8") as f:
    json.dump(parsed_containers, f, indent=2)

# Check missing RLUs
missing_rlu = [c for c in parsed_containers if c["rlu"] is None]
print(f"Containers with missing RLU: {len(missing_rlu)}")
if missing_rlu:
    for m in missing_rlu[:5]:
        print("  Missing RLU row:", m["page"], m["etx"], m["raw"])
