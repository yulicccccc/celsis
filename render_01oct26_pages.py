import os
import fitz

pdf_path = r"C:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Desktop\svc-scan@eagleanalytical.com_20261001_150052.pdf"
out_dir = r"C:\Users\qchen\temp_celsis_01oct26"
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)
print(f"Rendering {len(doc)} pages at 300 DPI to {out_dir} ...")

zoom = 300 / 72
mat = fitz.Matrix(zoom, zoom)

for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=mat)
    out_path = os.path.join(out_dir, f"page_{i+1:02d}.png")
    pix.save(out_path)
    print(f"Rendered page {i+1:02d} -> {out_path} ({pix.width}x{pix.height})")

print("All pages rendered successfully!")
