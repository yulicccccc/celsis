import os
import re
import fitz
import pytesseract
from PIL import Image
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

PDF_PATH = r"C:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\svc-scan@eagleanalytical.com_20260909_153050.pdf"
doc = fitz.open(PDF_PATH)

def parse_page_table(page_idx):
    page = doc[page_idx]
    pix = page.get_pixmap(dpi=300)
    w, h = pix.width, pix.height
    
    # We want to crop from 18% to 88% height
    crop_rect = (0, int(h * 0.18), w, int(h * 0.88))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    table_img = img.crop(crop_rect)
    
    # Let's run image_to_data
    data = pytesseract.image_to_data(table_img, output_type=pytesseract.Output.DATAFRAME)
    data = data[data.text.notnull() & (data.text.str.strip() != '')]
    return data

# Let's test on page 6 (0-indexed 5) and page 7 (0-indexed 6)
d6 = parse_page_table(5)
print("Page 6 data sample count:", len(d6))

# Let's cluster words by line based on top coordinate
# In table_img, lines are roughly separated by ~40-60 pixels
d6 = d6.sort_values(by=['top', 'left'])

lines = []
curr_line = []
curr_top = None

for _, row in d6.iterrows():
    if curr_top is None:
        curr_top = row['top']
        curr_line.append(row)
    elif abs(row['top'] - curr_top) <= 15:
        curr_line.append(row)
    else:
        lines.append(pd.DataFrame(curr_line).sort_values(by='left'))
        curr_line = [row]
        curr_top = row['top']
if curr_line:
    lines.append(pd.DataFrame(curr_line).sort_values(by='left'))

print(f"Total lines found on page 6: {len(lines)}")
for l in lines:
    words = l['text'].tolist()
    line_str = " ".join(words)
    if any(k in line_str for k in ["control", "ETX", "Cal", "Negative", "Positive"]):
        print(f"[{l['top'].iloc[0]}] {line_str}")
