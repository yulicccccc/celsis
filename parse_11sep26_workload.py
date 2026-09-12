import os
import sys
import re
import json
import cv2
import numpy as np
import pytesseract
from PIL import Image
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8")
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

PAGE_INFO = {
    # Instrument #2222
    6:  ("2222", "TSB"),
    7:  ("2222", "FTM"),
    8:  ("2222", "TSB"),
    9:  ("2222", "FTM"),
    10: ("2222", "TSB"),
    11: ("2222", "FTM"),
    12: ("2222", "TSB"),
    13: ("2222", "FTM"),
    # Instrument #2011
    17: ("2011", "TSB"),
    18: ("2011", "FTM"),
    19: ("2011", "TSB"),
    20: ("2011", "FTM"),
    21: ("2011", "TSB"),
    22: ("2011", "FTM"),
    23: ("2011", "TSB"),
    24: ("2011", "FTM"),
    25: ("2011", "TSB"),
    26: ("2011", "FTM"),
    27: ("2011", "TSB"),
    28: ("2011", "FTM"),
}

DAILY_ATP = {
    "2222": "93229",
    "2011": "82976"
}

TEMP_DIR = os.path.join(os.path.expanduser("~"), "temp_celsis_11sep26")

def clean_etx(raw):
    m = re.search(r"ET[X|K|R][- ]?(\d{6})[- ]?(\d{4})", raw, re.I)
    if not m:
        return None
    d1, d2 = m.group(1), m.group(2)
    if d1.startswith("20"):
        d1 = "26" + d1[2:]
    if d1 == "260001": d1 = "260901"
    if d1 == "260002": d1 = "260902"
    if d1 == "260003": d1 = "260903"
    if d1 == "260837": d1 = "260831"
    if d1 == "260887": d1 = "260831"
    if d1 == "260810": d1 = "260818"
    return f"ETX-{d1}-{d2}"

def process_single_page(pno, inst, media):
    img_path = os.path.join(TEMP_DIR, f"page_{pno}.png")
    if not os.path.exists(img_path):
        return []
        
    im = cv2.imread(img_path)
    h, w, _ = im.shape
    
    # Table bounding box: between 15% and 88% height
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

    results = []
    for idx, (sy, ey) in enumerate(row_bands):
        pad = 3
        r_sy = max(0, sy - pad)
        r_ey = min(table.shape[0], ey + pad)
        row_img = table[r_sy:r_ey, :]
        row_pil = Image.fromarray(cv2.cvtColor(row_img, cv2.COLOR_BGR2RGB))
        txt = pytesseract.image_to_string(row_pil, config="--psm 6").strip()
        
        if not txt:
            continue
            
        results.append({
            "page": pno,
            "inst": inst,
            "media": media,
            "text": txt
        })
    return results

def main():
    print("=" * 75)
    print("  Parallel Row Extraction for 11SEP26 Workload Pages (20 pages)")
    print("=" * 75)

    all_rows = []
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_single_page, pno, inst, media): pno for pno, (inst, media) in PAGE_INFO.items()}
        for future in as_completed(futures):
            pno = futures[future]
            try:
                page_rows = future.result()
                all_rows.extend(page_rows)
                print(f"Page {pno:02d}: Extracted {len(page_rows)} rows", flush=True)
            except Exception as e:
                print(f"Error on page {pno}: {e}", flush=True)

    with open("celsis_110926_all_rows_debug.json", "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    print(f"\nTotal extracted table rows: {len(all_rows)}")
    print("Parsing sample records...")

    sample_dict = defaultdict(lambda: {
        "TSB_RLUs": [],
        "FTM_RLUs": [],
        "CVs": [],
        "results": [],
        "inst": None,
        "pages": set(),
        "raw_entries": []
    })

    for r in all_rows:
        txt = r["text"]
        pno = r["page"]
        inst = r["inst"]
        media = r["media"]
        
        etx = clean_etx(txt)
        if not etx:
            continue
            
        # Parse numbers: RLU1, RLU2, RLU
        # Looking for pattern: RLU1 | RLU2 | RLU | Result
        m_r = re.search(r"(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([A-Za-z\s]+)", txt)
        rlu = None
        res_str = "Negative"
        cv = 0
        
        if m_r:
            r1 = int(m_r.group(1))
            r2 = int(m_r.group(2))
            rlu = int(m_r.group(3))
            res_str = m_r.group(4).strip()
            mean = (r1 + r2) / 2.0
            diff = abs(r1 - r2)
            cv = round((diff / (mean * (2 ** 0.5))) * 100) if mean > 0 else 0
        else:
            # Fallback: search for Negative and numbers
            nums = re.findall(r"\b\d{2,6}\b", txt)
            if nums and "negative" in txt.lower():
                rlu = int(nums[-1])
                res_str = "Negative"
            elif "overload" in txt.lower():
                rlu = 9999999
                res_str = "Overload"
            elif "positive" in txt.lower():
                res_str = "Positive"
                
        # Parse printed CV if available at end of row
        m_cv = re.search(r"\|\s*(\d{1,2})\s*[\|\]\}]", txt)
        if m_cv:
            try:
                printed_cv = int(m_cv.group(1))
                if printed_cv <= 40: # protect against merged border
                    cv = printed_cv
            except Exception:
                pass

        sample_dict[etx]["inst"] = inst
        sample_dict[etx]["pages"].add(pno)
        sample_dict[etx]["raw_entries"].append(txt)
        sample_dict[etx]["results"].append(res_str)
        if cv is not None:
            sample_dict[etx]["CVs"].append(cv)
            
        if media == "TSB" and rlu:
            sample_dict[etx]["TSB_RLUs"].append(rlu)
        elif media == "FTM" and rlu:
            sample_dict[etx]["FTM_RLUs"].append(rlu)

    print(f"\nAggregated {len(sample_dict)} unique samples.")

    # Build final database
    final_db = []
    for sid, d in sorted(sample_dict.items()):
        inst = d["inst"]
        atp = DAILY_ATP.get(inst, "UNKNOWN")
        max_tsb = max(d["TSB_RLUs"]) if d["TSB_RLUs"] else None
        max_ftm = max(d["FTM_RLUs"]) if d["FTM_RLUs"] else None
        max_cv = max(d["CVs"]) if d["CVs"] else 0
        pages = sorted(list(d["pages"]))
        
        status = "PASS"
        notes = "100% Valid Negative"
        
        if any("positive" in r.lower() for r in d["results"]):
            status = "BLOCK (Positive Result)"
            notes = "Replicate flagged Positive"
        elif any("overload" in r.lower() for r in d["results"]) or max_tsb == 9999999 or max_ftm == 9999999:
            status = "EXCLUDED (Instrument Overload)"
            notes = "Instrument Overload"
        elif max_cv >= 30:
            status = f"BLOCK (CV {max_cv}% >= 30%)"
            notes = f"Max CV% {max_cv}% >= 30%"
            
        final_db.append({
            "Sample": sid,
            "Instrument": inst,
            "Daily ATP": atp,
            "Max TSB RLU": max_tsb,
            "Max FTM RLU": max_ftm,
            "Max CV%": f"{max_cv}%",
            "Pages": pages,
            "Status": status,
            "Notes": notes
        })

    with open("celsis_110926_database.json", "w", encoding="utf-8") as f:
        json.dump(final_db, f, indent=2)

    print("=" * 75)
    print(f"🎉 Database built: celsis_110926_database.json ({len(final_db)} samples)")
    pass_cnt = sum(1 for s in final_db if s["Status"] == "PASS")
    block_cnt = sum(1 for s in final_db if "BLOCK" in s["Status"])
    excl_cnt = sum(1 for s in final_db if "EXCLUDED" in s["Status"])
    print(f"  • PASS:     {pass_cnt}")
    print(f"  • BLOCK:    {block_cnt}")
    print(f"  • EXCLUDED: {excl_cnt}")
    print("=" * 75)

if __name__ == "__main__":
    main()
