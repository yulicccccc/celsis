import json

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} pages.")
for p in pages:
    p_num = p["page_num"]
    p_of = p["page_of"]
    wl = p["wl_name"]
    batch = p["batch"]
    cutoff = p["neg_cutoff"]
    rows = p["rows"]
    print(f"Page {p_num:02d} ({p_of}) | WL: {wl} | Batch: {batch} | Cutoff: {cutoff} | Rows: {len(rows)}")
    for r in rows[:2]:
        print("    ", r["raw_text"])
    if len(rows) > 2:
        print("    ...")
        print("    ", rows[-1]["raw_text"])
