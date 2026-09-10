import os
import re
import fitz
import pytesseract
from PIL import Image
import pandas as pd
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

PDF_PATH = r"C:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\svc-scan@eagleanalytical.com_20260909_153050.pdf"
doc = fitz.open(PDF_PATH)

parsed_batches = []

for page_idx in range(len(doc)):
    page_num = page_idx + 1
    page = doc[page_idx]
    
    # 1. Header OCR
    pix_header = page.get_pixmap(dpi=200, clip=fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.22))
    img_header = Image.frombytes("RGB", [pix_header.width, pix_header.height], pix_header.samples)
    text_header = pytesseract.image_to_string(img_header)
    
    wl_m = re.search(r"Workload\s*Report:\s*([^\r\n]+)", text_header, re.I)
    wl_name = wl_m.group(1).strip() if wl_m else "UNKNOWN"
    
    batch_m = re.search(r"Batch:\s*([A-Za-z0-9]+)", text_header, re.I)
    batch_letter = batch_m.group(1).strip() if batch_m else ""
    
    assay_m = re.search(r"Assay\s*Name:\s*([^\r\n|]+)", text_header, re.I)
    assay_name = assay_m.group(1).strip() if assay_m else ""
    
    neg_cut_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", text_header, re.I)
    neg_cutoff = float(neg_cut_m.group(1)) if neg_cut_m else None
    
    pos_cut_m = re.search(r"Positive\s*Cut-off:\s*([0-9.]+)", text_header, re.I)
    pos_cutoff = float(pos_cut_m.group(1)) if pos_cut_m else None
    
    analyst_m = re.search(r"Analyst:\s*([A-Za-z0-9_]+)", text_header, re.I)
    analyst = analyst_m.group(1).strip() if analyst_m else ""
    
    date_m = re.search(r"Assay\s*Date/Time:\s*([^\r\n|]+)", text_header, re.I)
    assay_dt = date_m.group(1).strip() if date_m else ""
    
    # 2. Table OCR
    # clip table region: 16% to 88%
    pix_table = page.get_pixmap(dpi=250, clip=fitz.Rect(0, page.rect.height * 0.16, page.rect.width, page.rect.height * 0.88))
    img_table = Image.frombytes("RGB", [pix_table.width, pix_table.height], pix_table.samples)
    
    # We use tesseract image_to_string with --psm 6 and also image_to_data for fine structure
    table_text = pytesseract.image_to_string(img_table)
    
    page_info = {
        "page_num": page_num,
        "wl_name": wl_name,
        "batch": batch_letter,
        "assay_name": assay_name,
        "neg_cutoff": neg_cutoff,
        "pos_cutoff": pos_cutoff,
        "analyst": analyst,
        "assay_dt": assay_dt,
        "raw_table_text": table_text
    }
    parsed_batches.append(page_info)

with open("all_pages_raw.json", "w", encoding="utf-8") as f:
    json.dump(parsed_batches, f, indent=2)

print("Parsed and saved all_pages_raw.json")
