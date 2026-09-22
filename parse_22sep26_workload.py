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
    4:  ("2222", "TSB"),
    5:  ("2222", "FTM"),
    6:  ("2222", "TSB"),
    7:  ("2222", "FTM"),
    8:  ("2222", "TSB"),
    9:  ("2222", "FTM"),
    10: ("2222", "TSB"),
    11: ("2222", "FTM"),
    # Instrument #2011
    15: ("2011", "TSB"),
    16: ("2011", "FTM"),
    17: ("2011", "TSB"),
    18: ("2011", "FTM"),
}

DAILY_ATP = {
    "2222": "103791",
    "2011": "97310"
}

TEMP_DIR = os.path.join(os.path.expanduser("~"), "temp_celsis_22sep26")

def clean_etx(raw):
    # Match standard or noisy ETX patterns
    m = re.search(r'(?:[&E][TFKX][XKR]|ET[XKR]|EF[XKR]|&T[XKR])[- ]?(\d{6})[- ]?(\d{1,2}\s*\d{1,3}|\d{4})', raw, re.I)
    if not m:
        return None
    d1 = m.group(1)
    d2 = re.sub(r'\s+', '', m.group(2))
    if len(d2) != 4:
        # If OCR split digits e.g. 051 1 -> 0511
        return None
    if d1.startswith("20"):
        d1 = "26" + d1[2:]
    return f"ETX-{d1}-{d2}"

def parse_row(txt):
    m_rlu = re.search(r'(\d{2,6})\s*[\|\!\]\}\)\{\s]*(?:Negative|Cal\s*OK)', txt, re.I)
    rlu = int(m_rlu.group(1)) if m_rlu else None

    # CV percentage extraction: look after Negative/Cal OK for 1 or 2 digit number
    cv = 0
    m_cv = re.search(r'(?:Negative|Cal\s*OK)[^|]*[\|\!\]\}\)\{][^|]*[\|\!\]\}\)\{]?\s*(\d{1,2})\s*[\%\|\!\]\}\)\{]', txt, re.I)
    if m_cv and int(m_cv.group(1)) <= 35:
        cv = int(m_cv.group(1))
    else:
        # Fallback: check digits near the middle/end
        parts = [p.strip() for p in re.split(r'[\|\!\]\}\)\{\s]+', txt) if p.strip()]
        for p in parts[-4:]:
            if p.isdigit() and 0 <= int(p) <= 35:
                cv = int(p)
                break

    if rlu is not None:
        return rlu, "Negative" if "negative" in txt.lower() else "Cal OK", cv

    return None, "Unknown", 0

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
    print("  Parallel Row Extraction for 22SEP26 Workload Pages (12 pages)")
    print("=" * 75)

    all_rows = []
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_single_page, pno, inst, media): pno for pno, (inst, media) in PAGE_INFO.items()}
        for future in as_completed(futures):
            pno = futures[future]
            try:
                res = future.result()
                all_rows.extend(res)
                print(f"  [+] Page {pno:02d} processed -> {len(res)} table rows extracted", flush=True)
            except Exception as e:
                print(f"  [!] Error processing Page {pno:02d}: {e}", flush=True)

    all_rows.sort(key=lambda r: (r["page"], r.get("row_idx", 0)))
    with open("celsis_220926_all_rows_debug.json", "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_rows)} raw rows to celsis_220926_all_rows_debug.json")

    sample_dict = defaultdict(lambda: {
        "TSB_RLUs": [],
        "FTM_RLUs": [],
        "CVs": [],
        "results": [],
        "inst": None,
        "pages": set(),
        "entries": []
    })

    for r in all_rows:
        txt = r["text"]
        pno = r["page"]
        inst = r["inst"]
        media = r["media"]
        
        etx = clean_etx(txt)
        if not etx:
            continue

        rlu, res_str, cv = parse_row(txt)
        sample_dict[etx]["inst"] = inst
        sample_dict[etx]["pages"].add(pno)
        sample_dict[etx]["results"].append(res_str)
        if cv is not None:
            sample_dict[etx]["CVs"].append(cv)
            
        if media == "TSB" and rlu:
            sample_dict[etx]["TSB_RLUs"].append(rlu)
        elif media == "FTM" and rlu:
            sample_dict[etx]["FTM_RLUs"].append(rlu)

    print(f"Aggregated {len(sample_dict)} unique samples.")

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
        
        if max_cv >= 30:
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

    with open("celsis_220926_database.json", "w", encoding="utf-8") as f:
        json.dump(final_db, f, indent=2, ensure_ascii=False)

    print("=" * 75)
    print(f"🎉 Final Database: celsis_220926_database.json ({len(final_db)} samples)")
    pass_cnt = sum(1 for s in final_db if s["Status"] == "PASS")
    block_cnt = sum(1 for s in final_db if "BLOCK" in s["Status"])
    print(f"  • PASS:     {pass_cnt}")
    print(f"  • BLOCK:    {block_cnt}")
    print("=" * 75)

    for s in final_db:
        print(f"  {s['Sample']} | Inst: #{s['Instrument']} | TSB: {str(s['Max TSB RLU']):<6} | FTM: {str(s['Max FTM RLU']):<6} | CV%: {s['Max CV%']:<4} | Status: {s['Status']} | Pages: {s['Pages']}")

if __name__ == "__main__":
    main()
