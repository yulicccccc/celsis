import fitz
import os

pdf_path = r"G:\CRO\Celsis Sterility Packets\2026\09-2026\10SEP26.pdf"
out_dir = r"G:\CRO\temp_celsis"
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}", flush=True)

for p in range(1, len(doc) + 1):
    out_fn = os.path.join(out_dir, f"page_{p}.png")
    if not os.path.exists(out_fn):
        pix = doc[p-1].get_pixmap(dpi=150)
        pix.save(out_fn)
        print(f"Rendered Page {p} -> {out_fn}", flush=True)
    else:
        print(f"Page {p} already exists.", flush=True)

print("All 27 pages rendered on G: drive!", flush=True)
