import os
import re
import fitz
import cv2
import numpy as np
import pytesseract
from PIL import Image
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
PDF_PATH = r"G:\CRO\Celsis Sterility Packets\2026\09-2026\10SEP26.pdf"

doc = fitz.open(PDF_PATH)
print(f"Opened PDF: {PDF_PATH}, Total pages: {len(doc)}", flush=True)

all_pages_data = []

def extract_rows_from_page(page, page_num):
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w, _ = img.shape

    # 1. Header (top 20%)
    header_crop = img[0:int(h * 0.20), :]
    header_pil = Image.fromarray(cv2.cvtColor(header_crop, cv2.COLOR_BGR2RGB))
    header_text = pytesseract.image_to_string(header_pil)

    wl_m = re.search(r"Workload\s*Report:\s*([^\r\n]+)", header_text, re.I)
    wl_name = wl_m.group(1).strip() if wl_m else "UNKNOWN"

    batch_m = re.search(r"Batch:\s*([A-Za-z0-9]+)", header_text, re.I)
    batch = batch_m.group(1).strip() if batch_m else ""

    assay_m = re.search(r"Assay\s*Name:\s*([^\r\n|]+)", header_text, re.I)
    assay_name = assay_m.group(1).strip() if assay_m else ""

    neg_cut_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", header_text, re.I)
    neg_cutoff = float(neg_cut_m.group(1)) if neg_cut_m else None

    pos_cut_m = re.search(r"Positive\s*Cut-off:\s*([0-9.]+)", header_text, re.I)
    pos_cutoff = float(pos_cut_m.group(1)) if pos_cut_m else None

    analyst_m = re.search(r"Analyst:\s*([A-Za-z0-9_]+)", header_text, re.I)
    analyst = analyst_m.group(1).strip() if analyst_m else ""

    dt_m = re.search(r"Assay\s*Date/Time:\s*([^\r\n|]+)", header_text, re.I)
    assay_dt = dt_m.group(1).strip() if dt_m else ""

    # Footer (bottom 10%)
    footer_crop = img[int(h * 0.90):, :]
    footer_pil = Image.fromarray(cv2.cvtColor(footer_crop, cv2.COLOR_BGR2RGB))
    footer_text = pytesseract.image_to_string(footer_pil)
    page_of_m = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", footer_text, re.I)
    page_of = f"Page {page_of_m.group(1)} of {page_of_m.group(2)}" if page_of_m else f"Page {page_num}"

    # 2. Table Area (from 16% to 88%)
    table_top = int(h * 0.16)
    table_bot = int(h * 0.88)
    table_crop = img[table_top:table_bot, :]
    
    gray = cv2.cvtColor(table_crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]

    # Remove vertical lines
    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))
    vert_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vert_kernel)
    no_vert = cv2.subtract(binary, vert_lines)

    # Horizontal projection
    proj = np.sum(no_vert, axis=1)
    row_bands = []
    in_line = False
    start_y = 0
    for y, val in enumerate(proj):
        if val > 4000 and not in_line:
            in_line = True
            start_y = y
        elif val <= 4000 and in_line:
            in_line = False
            if y - start_y > 15:
                row_bands.append((start_y, y))

    parsed_rows = []
    for (sy, ey) in row_bands:
        pad = 6
        r_sy = max(0, sy - pad)
        r_ey = min(table_crop.shape[0], ey + pad)
        row_img = table_crop[r_sy:r_ey, :]
        row_pil = Image.fromarray(cv2.cvtColor(row_img, cv2.COLOR_BGR2RGB))
        row_text = pytesseract.image_to_string(row_pil, config="--psm 7").strip()
        if not row_text:
            continue
        
        # Skip table header rows
        if any(k in row_text.lower() for k in ["replicate", "bkgnd", "read time", "read date", "cv pct"]):
            continue
        if "Sample" in row_text and "Product" in row_text:
            continue

        parsed_rows.append({
            "raw_text": row_text,
            "y_range": (table_top + sy, table_top + ey)
        })

    return {
        "page_num": page_num,
        "wl_name": wl_name,
        "batch": batch,
        "assay_name": assay_name,
        "neg_cutoff": neg_cutoff,
        "pos_cutoff": pos_cutoff,
        "analyst": analyst,
        "assay_dt": assay_dt,
        "page_of": page_of,
        "rows": parsed_rows
    }

for idx in range(len(doc)):
    pnum = idx + 1
    print(f"Scanning Page {pnum:02d}/{len(doc)}...", flush=True)
    pdata = extract_rows_from_page(doc[idx], pnum)
    all_pages_data.append(pdata)

with open("celsis_100926_rows_extracted.json", "w", encoding="utf-8") as f:
    json.dump(all_pages_data, f, indent=2)

print("\nSaved celsis_100926_rows_extracted.json successfully!", flush=True)
