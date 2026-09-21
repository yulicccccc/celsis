import os
import glob
import re
import io
import json
import fitz
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

FOLDER = r"G:\CRO\Celsis Sterility Packets\2026\08-2026"
OUTPUT_FILE = "august_pdf_samples_summary.json"

def normalize_sid(sid):
    m = re.match(r"ET[X|K|R]-(\d{6})-(\d{4})", sid, re.I)
    if m:
        d1, d2 = m.group(1), m.group(2)
        if d1.startswith("2606"):
            d1 = "2608" + d1[4:]
        if d1.startswith("20"):
            d1 = "26" + d1[2:]
        return f"ETX-{d1}-{d2}"
    return sid

def process_page(args):
    pdf_path, page_idx, img_bytes = args
    try:
        img = Image.open(io.BytesIO(img_bytes))
        txt = pytesseract.image_to_string(img)
        matches = re.findall(r"ET[X|K|R][- ]?(\d{6})[- ]?(\d{4})", txt, re.I)
        cleaned = set()
        for d1, d2 in matches:
            if d1.startswith("20"):
                d1 = "26" + d1[2:]
            if d1.startswith("2606"):
                d1 = "2608" + d1[4:]
            cleaned.add(f"ETX-{d1}-{d2}")
        return pdf_path, page_idx, cleaned
    except Exception as e:
        print(f"Error on {pdf_path} page {page_idx}: {e}")
        return pdf_path, page_idx, set()

def main():
    print("=" * 75)
    print("  August 2026 Celsis PDF Sample Extractor (8 Workers)")
    print("=" * 75)

    pdf_files = sorted(glob.glob(os.path.join(FOLDER, "*.pdf")))
    print(f"Found {len(pdf_files)} PDF files in {FOLDER}.\n")

    all_tasks = []
    print("Rendering PDF pages to memory...")
    for p in pdf_files:
        doc = fitz.open(p)
        print(f" -> {os.path.basename(p):<25}: {len(doc)} pages")
        for i in range(len(doc)):
            # 150 DPI is optimal balance between OCR accuracy and rendering speed
            pix = doc[i].get_pixmap(dpi=150)
            all_tasks.append((p, i + 1, pix.tobytes("png")))

    print(f"\nTotal pages to OCR across {len(pdf_files)} PDFs: {len(all_tasks)}")
    print("Starting 8-worker parallel OCR processing...\n")

    results_by_pdf = {p: set() for p in pdf_files}
    completed_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_page, task) for task in all_tasks]
        for f in as_completed(futures):
            pdf_path, pno, samples = f.result()
            results_by_pdf[pdf_path].update(samples)
            completed_count += 1
            if completed_count % 25 == 0 or completed_count == len(all_tasks):
                print(f"  [{completed_count:03d}/{len(all_tasks):03d}] pages processed ({(completed_count/len(all_tasks)*100):.1f}%)...", flush=True)

    summary = {}
    print("\n" + "=" * 60)
    print("  August Extraction Summary:")
    print("=" * 60)
    total_unique_all = set()
    for p in pdf_files:
        bname = os.path.basename(p)
        s_list = sorted(list(results_by_pdf[p]))
        summary[bname] = s_list
        total_unique_all.update(s_list)
        print(f"  • {bname:<25}: {len(s_list):2d} unique ETX samples found")

    print("=" * 60)
    print(f"Total unique ETX samples across all 23 PDFs in August: {len(total_unique_all)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved full sample mapping to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
