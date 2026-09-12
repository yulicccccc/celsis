import os
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
temp_dir = os.path.join(os.path.expanduser('~'), 'temp_celsis_11sep26')

for p in range(17, 29):
    img = Image.open(os.path.join(temp_dir, f'page_{p}.png'))
    w, h = img.size
    crop = img.crop((0, 0, w, int(h * 0.16)))
    txt = pytesseract.image_to_string(crop).strip()
    first_lines = [l.strip() for l in txt.splitlines() if l.strip()][:3]
    print(f"Page {p:02d}: {' || '.join(first_lines)}")
