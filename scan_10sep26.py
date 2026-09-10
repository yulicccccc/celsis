import os
import sys
import re
import fitz
import pytesseract
from PIL import Image
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
PDF_PATH = r"G:\CRO\Celsis Sterility Packets\2026\09-2026\10SEP26.pdf"

if not os.path.exists(PDF_PATH):
    print(f"Error: {PDF_PATH} does not exist!")
    sys.exit(1)

doc = fitz.open(PDF_PATH)
print(f"Opened {PDF_PATH}, total pages: {len(doc)}", flush=True)

pages_data = []

for idx in range(len(doc)):
    page_num = idx + 1
    page = doc[idx]
    
    # Header clip
    pix_header = page.get_pixmap(dpi=150, clip=fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.22))
    img_header = Image.frombytes("RGB", [pix_header.width, pix_header.height], pix_header.samples)
    text_header = pytesseract.image_to_string(img_header)
    
    wl_m = re.search(r"Workload\s*Report:\s*([^\r\n]+)", text_header, re.I)
    wl_name = wl_m.group(1).strip() if wl_m else "UNKNOWN"
    
    daily_m = re.search(r"Daily\s*Control", text_header, re.I)
    is_daily = bool(daily_m)
    
    batch_m = re.search(r"Batch:\s*([A-Za-z0-9]+)", text_header, re.I)
    batch_letter = batch_m.group(1).strip() if batch_m else ""
    
    inst_m = re.search(r"Instrument(?:\s*Type)?:\s*([^\r\n|]+)", text_header, re.I)
    inst = inst_m.group(1).strip() if inst_m else ""
    
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
    
    # Table OCR (16% to 88%)
    pix_table = page.get_pixmap(dpi=200, clip=fitz.Rect(0, page.rect.height * 0.16, page.rect.width, page.rect.height * 0.88))
    img_table = Image.frombytes("RGB", [pix_table.width, pix_table.height], pix_table.samples)
    table_text = pytesseract.image_to_string(img_table)
    
    # Footer OCR (88% to 100%)
    pix_footer = page.get_pixmap(dpi=150, clip=fitz.Rect(0, page.rect.height * 0.88, page.rect.width, page.rect.height))
    img_footer = Image.frombytes("RGB", [pix_footer.width, pix_footer.height], pix_footer.samples)
    footer_text = pytesseract.image_to_string(img_footer)
    
    page_info = {
        "page_num": page_num,
        "wl_name": wl_name,
        "is_daily": is_daily,
        "batch": batch_letter,
        "inst": inst,
        "assay_name": assay_name,
        "neg_cutoff": neg_cutoff,
        "pos_cutoff": pos_cutoff,
        "analyst": analyst,
        "assay_dt": assay_dt,
        "footer_text": footer_text,
        "table_text": table_text
    }
    pages_data.append(page_info)
    print(f"[{page_num:02d}/27] Page {page_num:02d}: WL='{wl_name}' | Batch={batch_letter} | Inst={inst} | Daily={is_daily}", flush=True)

with open("celsis_100926_pages_raw.json", "w", encoding="utf-8") as f:
    json.dump(pages_data, f, indent=2)

print("\nSaved all 27 pages to celsis_100926_pages_raw.json", flush=True)
