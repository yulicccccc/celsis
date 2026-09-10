import json
import re
from collections import defaultdict

DAILY_ATP = {
    "2222": "92940",
    "2011": "92099"
}

with open("celsis_100926_pages_raw.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} pages from celsis_100926_pages_raw.json")

# Mapping pages to Instrument and Media
# Let's inspect each workload page's media and controls
page_meta = {}
for p in pages:
    pno = p["page_num"]
    wl = p["wl_name"]
    is_daily = p["is_daily"]
    if is_daily:
        continue
        
    inst = "2222" if "2222" in wl else ("2011" if "2011" in wl else "UNKNOWN")
    
    # Detect media from table text
    txt = p["table_text"]
    media = "UNKNOWN"
    if "tsb" in txt.lower():
        media = "TSB"
    elif "ftm" in txt.lower():
        media = "FTM"
        
    page_meta[pno] = {
        "inst": inst,
        "wl": wl,
        "media": media,
        "batch": p["batch"],
        "cutoff": p["neg_cutoff"]
    }

# Specific manual overrides for pages where OCR on controls was ambiguous
# Let's check pages 5-12 (2222) and 16-27 (2011)
page_media_map = {
    5: "TSB", 6: "FTM",
    7: "TSB", 8: "FTM",
    9: "TSB", 10: "FTM",
    11: "TSB", 12: "FTM",
    16: "TSB", 17: "FTM",
    18: "TSB", 19: "TSB", 20: "FTM", 21: "FTM",
    22: "TSB", 23: "FTM",
    24: "TSB", 25: "FTM",
    26: "TSB", 27: "FTM"
}

for pno, med in page_media_map.items():
    if pno in page_meta:
        page_meta[pno]["media"] = med

def normalize_etx(raw):
    m = re.search(r"ET[X|K|R][- ]?(\d{6})[- ]?(\d{4})", raw, re.I)
    if not m:
        return None
    d1, d2 = m.group(1), m.group(2)
    # Fix common OCR typos in date prefix
    if d1.startswith("20"):
        d1 = "26" + d1[2:]
    if d1 == "260001": d1 = "260901"
    if d1 == "260002": d1 = "260902"
    if d1 == "260837": d1 = "260831"
    if d1 == "260887": d1 = "260831"
    return f"ETX-{d1}-{d2}"

sample_data = defaultdict(lambda: {
    "TSB_readings": [],
    "FTM_readings": [],
    "CVs": [],
    "instruments": set(),
    "pages": set(),
    "raw_lines": [],
    "results": []
})

for p in pages:
    pno = p["page_num"]
    if pno not in page_meta:
        continue
    
    inst = page_meta[pno]["inst"]
    media = page_meta[pno]["media"]
    lines = p["table_text"].split("\n")
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        # Check if line contains ETX
        etx = normalize_etx(line_str)
        if not etx:
            continue
            
        sample_data[etx]["instruments"].add(inst)
        sample_data[etx]["pages"].add(pno)
        sample_data[etx]["raw_lines"].append((pno, line_str))
        
        # Check Result
        if "overload" in line_str.lower():
            sample_data[etx]["results"].append("Overload")
        elif "positive" in line_str.lower():
            sample_data[etx]["results"].append("Positive")
        elif "negative" in line_str.lower():
            sample_data[etx]["results"].append("Negative")
            
        # Extract RLU and CV Pct
        # Pattern 1: RLU1 | RLU2 | RLU | Result ... CV Pct
        # e.g., 2661 | 2613 | 2637 | Negative} 9/10/2026 | 10:14:08 AM 4 3
        # In this format, 3 numbers before negative/positive/cal ok
        m_r = re.search(r"(\d{2,7})\s*\|\s*(\d{2,7})\s*\|\s*(\d{2,7})\s*\|\s*(?:Negative|Positive|Cal OK|Overload)", line_str, re.I)
        if m_r:
            r1, r2, rlu = int(m_r.group(1)), int(m_r.group(2)), int(m_r.group(3))
            if media == "TSB":
                sample_data[etx]["TSB_readings"].append(rlu)
            elif media == "FTM":
                sample_data[etx]["FTM_readings"].append(rlu)
        else:
            # Single RLU fallback
            m_s = re.search(r"(\d{2,7})\s*\|\s*(?:Negative|Positive|Cal OK|Overload)", line_str, re.I)
            if m_s:
                rlu = int(m_s.group(1))
                if media == "TSB":
                    sample_data[etx]["TSB_readings"].append(rlu)
                elif media == "FTM":
                    sample_data[etx]["FTM_readings"].append(rlu)
                    
        # Extract CV Pct: column at the right
        # Look for numbers after AM/PM or after Result
        # e.g. "10:14:08 AM 4 3" -> 4 is CV Pct, 3 is Bkgnd
        m_time = re.search(r"\b(?:AM|PM)\b\s+(\d{1,2})\b", line_str, re.I)
        if m_time:
            cv_val = int(m_time.group(1))
            sample_data[etx]["CVs"].append(cv_val)
        else:
            # Check if CV is printed before or after negative
            m_cv_col = re.search(r"(?:Negative|Positive)\s*[:|\]}\s]+(?:\d{1,2}/\d{1,2}/\d{4}\s*[:|\]}\s]+[\d:]+\s*(?:AM|PM)\s*)?(\d{1,2})\b", line_str, re.I)
            if m_cv_col:
                try:
                    cv_val = int(m_cv_col.group(1))
                    sample_data[etx]["CVs"].append(cv_val)
                except:
                    pass

print(f"\nExtracted {len(sample_data)} unique samples from 10SEP26.pdf:")
samples_summary = []

for sid in sorted(sample_data.keys()):
    info = sample_data[sid]
    insts = list(info["instruments"])
    inst = insts[0] if insts else "UNKNOWN"
    atp = DAILY_ATP.get(inst, "UNKNOWN")
    tsb_max = max(info["TSB_readings"]) if info["TSB_readings"] else None
    ftm_max = max(info["FTM_readings"]) if info["FTM_readings"] else None
    cv_max = max(info["CVs"]) if info["CVs"] else None
    
    is_overload = "Overload" in info["results"]
    is_positive = "Positive" in info["results"]
    
    status = "PASS"
    notes = "Valid Negative"
    
    if sid == "ETX-260818-0652" or is_overload:
        status = "EXCLUDED (User Command: Overload/Special)"
        notes = "User explicitly instructed to skip ETX-260818-0652"
    elif is_positive:
        status = "BLOCK (Positive Result)"
        notes = "Sample tested positive"
    elif cv_max is not None and cv_max >= 30:
        status = f"BLOCK (CV {cv_max}% >= 30%)"
        notes = f"CV {cv_max}% failsafe triggered"
        
    record = {
        "Sample": sid,
        "Instrument": inst,
        "ATP Positive": atp,
        "Max TSB RLU": tsb_max,
        "Max FTM RLU": ftm_max,
        "Max CV%": f"{cv_max}%" if cv_max is not None else "N/A",
        "Pages": sorted(list(info["pages"])),
        "Status": status,
        "Notes": notes
    }
    samples_summary.append(record)
    print(f"  {sid:16} | Inst: #{inst} | ATP: {atp} | TSB: {str(tsb_max):>5} | FTM: {str(ftm_max):>5} | CV: {str(cv_max)+'%':>5} | Status: {status}")

with open("celsis_100926_parsed_summary.json", "w", encoding="utf-8") as f:
    json.dump(samples_summary, f, indent=2)

print(f"\nSaved {len(samples_summary)} samples to celsis_100926_parsed_summary.json")
