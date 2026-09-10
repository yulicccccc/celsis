import json
import re
from collections import defaultdict

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Instrument ATP anchors
DAILY_ATP = {
    "2222": 92047, # Page 3
    "2011": 95167  # Page 22
}

def clean_ocr_line(txt):
    t = txt
    # Fix common OCR typos in ETX prefix
    t = re.sub(r"ET[FfXx][ -]?", "ETX-", t)
    t = re.sub(r"ETX-?200902", "ETX-260902", t)
    t = re.sub(r"ETX-?2008", "ETX-2608", t)
    t = re.sub(r"ETX-?2009", "ETX-2609", t)
    t = re.sub(r"ETX-?260001", "ETX-260901", t)
    t = re.sub(r"ETX-?260887", "ETX-260831", t)
    t = re.sub(r"ETX-?260890", "ETX-260830", t)
    # Fix specific container digit glitches
    t = re.sub(r"ETX-260901-0228-\(3", "ETX-260901-0229-(3", t)
    t = re.sub(r"ETX-260901-0417-6", "ETX-260901-0411-(6", t)
    t = re.sub(r"ETX-260901-0602\(4", "ETX-260901-0692-(4", t)
    return t

all_parsed = []

for p in pages:
    pnum = p["page_num"]
    wl = p["wl_name"]
    batch = p["batch"]
    inst = "2222" if "2222" in wl else ("2011" if "2011" in wl else "UNKNOWN")
    
    # Check page cutoff & media
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
        
        # Check if control row
        if any(k in txt.lower() for k in ["control", "cal ok"]):
            continue
        if "inst" in txt.lower() or "reag" in txt.lower() or "atp" in txt.lower():
            continue
            
        m = re.search(r"ETX[- ]?(\d{6})[- ]?(\d{4})(?:[- /(]+(\d{1,2}))?", txt, re.IGNORECASE)
        if not m:
            continue
            
        clean_etx = f"ETX-{m.group(1)}-{m.group(2)}"
        container = m.group(3) if m.group(3) else "1"
        
        # Extract numbers and result
        # Line format typically: Pos | ETX... | RLU1 | RLU2 | RLU | Result | Date | Time | CV | Bkgnd
        # Let's extract RLU1, RLU2, RLU, CV
        tokens = [tk.strip() for tk in txt.split("|") if tk.strip()]
        
        # Let's extract integers
        # We can extract all integer sequences
        res = "Negative"
        if "Positive" in txt:
            res = "Positive"
            
        all_parsed.append({
            "page": pnum,
            "wl": wl,
            "batch": batch,
            "inst": inst,
            "media": media,
            "cutoff": cutoff,
            "etx": clean_etx,
            "container": container,
            "raw": txt,
            "result": res
        })

print(f"Total parsed entries: {len(all_parsed)}")
by_etx = defaultdict(list)
for rec in all_parsed:
    by_etx[rec["etx"]].append(rec)

print(f"Total unique ETX samples: {len(by_etx)}")
for etx in sorted(by_etx.keys()):
    recs = by_etx[etx]
    tsb_c = len([r for r in recs if r["media"] == "TSB"])
    ftm_c = len([r for r in recs if r["media"] == "FTM"])
    inst = recs[0]["inst"]
    print(f"  {etx} ({inst}): TSB={tsb_c}, FTM={ftm_c}, Pages={sorted(list(set(r['page'] for r in recs)))}")
