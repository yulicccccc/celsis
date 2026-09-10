import os
import sys
import fitz
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

PDF_PATH = r"C:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\svc-scan@eagleanalytical.com_20260909_153050.pdf"
CACHE_DIR = r"c:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\Celsis\ocr_cache_090926"

os.makedirs(CACHE_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)
print(f"Total pages in PDF: {len(doc)}")

for page_idx in range(len(doc)):
    page_num = page_idx + 1
    cache_file = os.path.join(CACHE_DIR, f"page_{page_num:02d}.txt")
    if os.path.exists(cache_file):
        print(f"Page {page_num} already cached.")
        continue
    
    print(f"Processing Page {page_num}/{len(doc)}...")
    page = doc[page_idx]
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # PSM 6 is good for uniform blocks of text, but let's do standard OCR or PSM 4/6
    text = pytesseract.image_to_string(img)
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(text)

print("OCR complete for all pages.")
