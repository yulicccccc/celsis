import os
import re
import io
import json
import fitz
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\qchen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

PDFS = [
    r"G:\CRO\Celsis Sterility Packets\2026\08-2026\31AUG26.pdf",
    r"G:\CRO\Celsis Sterility Packets\2026\09-2026\01SEP26.pdf",
    r"G:\CRO\Celsis Sterility Packets\2026\09-2026\02SEP26.pdf",
    r"G:\CRO\Celsis Sterility Packets\2026\09-2026\03SEP26.pdf",
    r"G:\CRO\Celsis Sterility Packets\2026\09-2026\04SEP26.pdf"
]

OUTPUT_FILE = "pdf_samples_summary.json"

def process_page(args):
    pdf_path, page_idx, img_bytes = args
    try:
        img = Image.open(io.BytesIO(img_bytes))
        # OCR using fast whitelist or default
        txt = pytesseract.image_to_string(img)
        matches = re.findall(r"ET[X|K|R][- ]?(\d{6})[- ]?(\d{4})", txt, re.I)
        cleaned = set()
        for d1, d2 in matches:
            if d1.startswith("20"):
                d1 = "26" + d1[2:]
            cleaned.add(f"ETX-{d1}-{d2}")
        return pdf_path, page_idx, cleaned
    except Exception as e:
        print(f"Error on {pdf_path} page {page_idx}: {e}")
        return pdf_path, page_idx, set()

def main():
    print("====================================================")
    print("  Fast Parallel Celsis PDF Sample Extractor (8 Workers)")
    print("====================================================")

    all_tasks = []
    print("Rendering PDF pages to memory...")
    for p in PDFS:
        doc = fitz.open(p)
        print(f" -> {os.path.basename(p)}: {len(doc)} pages")
        for i in range(len(doc)):
            # Render at 150 DPI for optimal speed and character clarity
            pix = doc[i].get_pixmap(dpi=150)
            all_tasks.append((p, i + 1, pix.tobytes("png")))

    print(f"\nTotal pages to OCR across 5 PDFs: {len(all_tasks)}")
    print("Starting parallel OCR processing...")

    results_by_pdf = {p: set() for p in PDFS}
    completed_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_page, task) for task in all_tasks]
        for f in as_completed(futures):
            pdf_path, pno, samples = f.result()
            results_by_pdf[pdf_path].update(samples)
            completed_count += 1
            if completed_count % 10 == 0 or completed_count == len(all_tasks):
                print(f"  [{completed_count:03d}/{len(all_tasks):03d}] pages processed...", flush=True)

    summary = {}
    print("\n" + "=" * 60)
    print("  Extraction Summary:")
    print("=" * 60)
    for p in PDFS:
        bname = os.path.basename(p)
        s_list = sorted(list(results_by_pdf[p]))
        summary[bname] = s_list
        print(f"  • {bname:<15}: {len(s_list):2d} unique ETX samples found")
        if s_list:
            print(f"    Sample preview: {', '.join(s_list[:4])} ...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved full sample mapping to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
