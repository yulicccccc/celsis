import fitz
import os

pdf_path = r"C:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Desktop\25SEP26.pdf"
out_dir = r"C:\Users\qchen\temp_celsis_25sep26"
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)
print(f"Total pages in {pdf_path}: {len(doc)}")

zoom = 300 / 72 # 300 DPI
mat = fitz.Matrix(zoom, zoom)

for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(matrix=mat)
    out_file = os.path.join(out_dir, f"page_{i+1:02d}.png")
    pix.save(out_file)
    print(f"Rendered Page {i+1:02d} -> {out_file}")

print("All pages rendered successfully!")
