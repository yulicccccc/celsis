import json
import re
from collections import defaultdict
import pandas as pd

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

DAILY_ATP = {
    "2222": 92047, # Page 3: 91100, 92993 -> 92047
    "2011": 95167  # Page 22: 100459, 89874 -> 95167
}

def clean_ocr_line(txt):
    t = txt
    t = re.sub(r"ET[A-Za-z]{1,2}[- ]*", "ETX-", t)
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
    t = re.sub(r"ETX-?260901\s*~0411-\(2", "ETX-260901-0411-(2", t)
    t = re.sub(r"ETX-?260901-041147", "ETX-260901-0411-(7", t)
    t = re.sub(r"ETX-?260901-0602\(4", "ETX-260901-0692-(4", t)
    return t

def solve_rlu_triplet(line_text):
    m_etx = re.search(r"ETX[- ]?\d{6}[- ]?\d{4}(?:[- /(]+\d{1,2})?", line_text, re.I)
    after_etx = line_text[m_etx.end():] if m_etx else line_text
    m_end = re.search(r"(?:Negative|Positive|Cal OK|9/\d/2026)", after_etx, re.I)
    val_part = after_etx[:m_end.start()] if m_end else after_etx
    
    cleaned = re.sub(r"[\|\[\]\{\}\(\)!:;jJ/\\]+", " ", val_part)
    tokens = cleaned.split()
    
    candidates = []
    for t in tokens:
        if t.isdigit():
            val = int(t)
            if len(t) == 8:
                candidates.append(int(t[:4]))
                candidates.append(int(t[4:]))
            elif len(t) == 9:
                candidates.append(int(t[:4]))
                candidates.append(int(t[5:]))
            elif len(t) == 10:
                candidates.append(int(t[:5]))
                candidates.append(int(t[5:]))
            else:
                if len(t) == 5 and t.startswith("1") and int(t[1:]) > 1000:
                    candidates.append(val)
                    candidates.append(int(t[1:]))
                else:
                    candidates.append(val)
                    
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            for k in range(j + 1, len(candidates)):
                n1, n2, m = candidates[i], candidates[j], candidates[k]
                if n1 >= 50 and n2 >= 50 and m >= 50:
                    expected_m = (n1 + n2) / 2.0
                    if abs(expected_m - m) <= 2:
                        return n1, n2, m
                        
    return None, None, None

def parse_line_full(txt):
    res = "Negative"
    if "Positive" in txt:
        res = "Positive"
    elif "Cal OK" in txt:
        res = "Cal OK"
        
    n1, n2, m = solve_rlu_triplet(txt)
    
    cv = None
    if n1 and n2 and m:
        mean_val = (n1 + n2) / 2.0
        if mean_val > 0:
            calc_cv = round((abs(n1 - n2) / (2**0.5)) / mean_val * 100.0, 1)
            cv = calc_cv
            
    return n1, n2, m, cv, res

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
        
        rlu1, rlu2, rlu, cv, res = parse_line_full(txt)
        
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
with open("parsed_containers_solved.json", "w", encoding="utf-8") as f:
    json.dump(parsed_containers, f, indent=2)
