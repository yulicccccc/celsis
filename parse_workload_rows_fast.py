import os
import sys
import re
import json
import cv2
import numpy as np
import pytesseract
from PIL import Image
from collections import defaultdict

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Page to (Instrument, Media) mapping
PAGE_INFO = {
    5:  ("2222", "TSB"),
    6:  ("2222", "FTM"),
    7:  ("2222", "TSB"),
    8:  ("2222", "FTM"),
    9:  ("2222", "TSB"),
    10: ("2222", "FTM"),
    11: ("2222", "TSB"),
    12: ("2222", "FTM"),
    16: ("2011", "TSB"),
    17: ("2011", "FTM"),
    18: ("2011", "TSB"),
    19: ("2011", "TSB"),
    20: ("2011", "FTM"),
    21: ("2011", "FTM"),
    22: ("2011", "TSB"),
    23: ("2011", "FTM"),
    24: ("2011", "TSB"),
    25: ("2011", "FTM"),
    26: ("2011", "TSB"),
    27: ("2011", "FTM"),
}

DAILY_ATP = {
    "2222": "92940",
    "2011": "92099"
}

def clean_etx(raw):
    m = re.search(r"ET[X|K|R][- ]?(\d{6})[- ]?(\d{4})", raw, re.I)
    if not m:
        return None
    d1, d2 = m.group(1), m.group(2)
    if d1.startswith("20"):
        d1 = "26" + d1[2:]
    if d1 == "260001": d1 = "260901"
    if d1 == "260002": d1 = "260902"
    if d1 == "260837": d1 = "260831"
    if d1 == "260887": d1 = "260831"
    if d1 == "260810": d1 = "260818" # OCR error on 0652
    return f"ETX-{d1}-{d2}"

sample_data = defaultdict(lambda: {
    "TSB_readings": [],
    "FTM_readings": [],
    "CVs": [],
    "instruments": set(),
    "pages": set(),
    "results": [],
    "containers": []
})

all_rows_debug = []

for pno, (inst, media) in sorted(PAGE_INFO.items()):
    img_path = rf"G:\CRO\temp_celsis\page_{pno}.png"
    if not os.path.exists(img_path):
        print(f"Warning: {img_path} not found!")
        continue
        
    im = cv2.imread(img_path)
    h, w, _ = im.shape
    
    # Table crop: 15% to 88%
    table = im[int(h * 0.15):int(h * 0.88), :]
    gray = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]

    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))
    vert_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vert_kernel)
    no_vert = cv2.subtract(binary, vert_lines)

    proj = np.sum(no_vert, axis=1)
    row_bands = []
    in_line = False
    start_y = 0
    for y, val in enumerate(proj):
        if val > 2000 and not in_line:
            in_line = True
            start_y = y
        elif val <= 2000 and in_line:
            in_line = False
            if y - start_y > 10:
                row_bands.append((start_y, y))

    print(f"Page {pno:02d} ({inst} {media}): found {len(row_bands)} row bands", flush=True)

    for idx, (sy, ey) in enumerate(row_bands):
        pad = 3
        r_sy = max(0, sy - pad)
        r_ey = min(table.shape[0], ey + pad)
        row_img = table[r_sy:r_ey, :]
        row_pil = Image.fromarray(cv2.cvtColor(row_img, cv2.COLOR_BGR2RGB))
        txt = pytesseract.image_to_string(row_pil, config="--psm 6").strip()
        
        if not txt:
            continue
            
        all_rows_debug.append({"page": pno, "inst": inst, "media": media, "text": txt})
        
        # Check if line contains ETX
        etx = clean_etx(txt)
        if not etx:
            continue
            
        sample_data[etx]["instruments"].add(inst)
        sample_data[etx]["pages"].add(pno)
        
        # Determine Result
        res = "Negative"
        if "overload" in txt.lower():
            res = "Overload"
        elif "positive" in txt.lower():
            res = "Positive"
        sample_data[etx]["results"].append(res)
        
        # Extract RLU values
        # Look for 3 numbers in a row
        nums = re.findall(r"\b\d{2,7}\b", txt)
        # Often: [Sample#, RLU1, RLU2, RLU, Date, Time, CV, Bkgnd]
        # Or: [RLU1, RLU2, RLU]
        # Let's find RLU1, RLU2, RLU
        m_r = re.search(r"(\d{2,7})\s*[|;\]}\s]+(\d{2,7})\s*[|;\]}\s]+(\d{2,7})\s*[|;\]}\s]*(?:Negative|Positive|Cal OK|Overload)", txt, re.I)
        if m_r:
            r1, r2, rlu = int(m_r.group(1)), int(m_r.group(2)), int(m_r.group(3))
            if media == "TSB":
                sample_data[etx]["TSB_readings"].append(rlu)
            elif media == "FTM":
                sample_data[etx]["FTM_readings"].append(rlu)
        else:
            # Look for numbers right before Negative/Positive
            m_before = re.search(r"(\d{2,7})\s*[|;\]}\s]*(?:Negative|Positive|Cal OK|Overload)", txt, re.I)
            if m_before:
                rlu = int(m_before.group(1))
                if media == "TSB":
                    sample_data[etx]["TSB_readings"].append(rlu)
                elif media == "FTM":
                    sample_data[etx]["FTM_readings"].append(rlu)

        # Extract CV Pct: integer after AM/PM or near end of line
        m_cv = re.search(r"\b(?:AM|PM)\b[|;\]}\s]+(\d{1,2})\b", txt, re.I)
        if m_cv:
            cv_val = int(m_cv.group(1))
            sample_data[etx]["CVs"].append(cv_val)
        else:
            m_cv2 = re.search(r"(?:Negative|Positive)\b[^\n\r]*?\b(\d{1,2})\s+\d{1,2}\s*$", txt, re.I)
            if m_cv2:
                sample_data[etx]["CVs"].append(int(m_cv2.group(1)))

print(f"\nTotal unique samples processed: {len(sample_data)}", flush=True)

# Build Master Database
master_records = []
for sid in sorted(sample_data.keys()):
    info = sample_data[sid]
    insts = list(info["instruments"])
    inst = insts[0] if insts else "UNKNOWN"
    atp = DAILY_ATP.get(inst, "UNKNOWN")
    
    tsb_max = max(info["TSB_readings"]) if info["TSB_readings"] else None
    ftm_max = max(info["FTM_readings"]) if info["FTM_readings"] else None
    cv_max = max(info["CVs"]) if info["CVs"] else None
    
    is_overload = "Overload" in info["results"] or sid in ["ETX-260818-0652", "ETX-260810-0052"]
    is_pos = "Positive" in info["results"]
    
    status = "PASS"
    notes = "100% Valid"
    
    if is_overload or sid == "ETX-260818-0652":
        status = "EXCLUDED (User Command: Overload/Special)"
        notes = "User instructed to skip ETX-260818-0652"
    elif is_pos:
        status = "BLOCK (Positive Result)"
        notes = "Positive result detected"
    elif cv_max is not None and cv_max >= 30:
        status = f"BLOCK (CV {cv_max}% >= 30%)"
        notes = f"CV {cv_max}% >= 30%"
        
    rec = {
        "Sample": sid,
        "Instrument": inst,
        "Daily ATP": atp,
        "Max TSB RLU": tsb_max,
        "Max FTM RLU": ftm_max,
        "Max CV%": f"{cv_max}%" if cv_max is not None else "N/A",
        "Pages": sorted(list(info["pages"])),
        "Status": status,
        "Notes": notes
    }
    master_records.append(rec)

with open("celsis_100926_database.json", "w", encoding="utf-8") as f:
    json.dump(master_records, f, indent=2)

with open("celsis_100926_all_rows_debug.json", "w", encoding="utf-8") as f:
    json.dump(all_rows_debug, f, indent=2)

print(f"Saved celsis_100926_database.json with {len(master_records)} samples!", flush=True)
