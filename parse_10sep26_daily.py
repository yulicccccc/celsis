import os
import sys
import re
import json
import fitz
import cv2
import numpy as np
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
PDF_PATH = r"G:\CRO\Celsis Sterility Packets\2026\09-2026\10SEP26.pdf"

doc = fitz.open(PDF_PATH)
print(f"Opened {PDF_PATH}, total pages: {len(doc)}", flush=True)

# 1. First, inspect Daily Control pages
daily_atp = {}

for pno in range(len(doc)):
    page = doc[pno]
    # Check top 20%
    pix_top = page.get_pixmap(dpi=150, clip=fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.22))
    img_top = Image.frombytes("RGB", [pix_top.width, pix_top.height], pix_top.samples)
    top_txt = pytesseract.image_to_string(img_top)
    
    if "daily control" in top_txt.lower():
        # Full table OCR for daily control
        pix_tbl = page.get_pixmap(dpi=200, clip=fitz.Rect(0, page.rect.height * 0.16, page.rect.width, page.rect.height * 0.88))
        img_tbl = Image.frombytes("RGB", [pix_tbl.width, pix_tbl.height], pix_tbl.samples)
        tbl_txt = pytesseract.image_to_string(img_tbl)
        
        # Determine instrument: 2222 or 2011
        inst = "UNKNOWN"
        if "2222" in top_txt or "2222" in tbl_txt:
            inst = "2222"
        elif "2011" in top_txt or "2011" in tbl_txt:
            inst = "2011"
            
        print(f"\n--- Daily Control on Page {pno+1} (Instrument: {inst}) ---", flush=True)
        for line in tbl_txt.splitlines():
            line_str = line.strip()
            if any(k in line_str.lower() for k in ["atp", "pos", "control", "cal ok"]):
                print("   ", line_str, flush=True)
                # Look for ATP Positive Control number
                # e.g., ATP,pos control 95167 or similar
                nums = re.findall(r"\b\d{4,6}\b", line_str)
                if "atp" in line_str.lower() and nums:
                    daily_atp[inst] = nums[-1]
                    print(f"    >>> Extracted ATP for #{inst}: {nums[-1]}", flush=True)

print("\nSummary of Daily Control ATP values:", daily_atp, flush=True)

# Save daily ATP to a json
with open("celsis_100926_daily_atp.json", "w", encoding="utf-8") as f:
    json.dump(daily_atp, f, indent=2)

