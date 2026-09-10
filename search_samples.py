import json

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

for p in pages:
    for r in p["rows"]:
        if "0813" in r["raw_text"]:
            print(f"Page {p['page_num']} ({p['wl_name']}, Batch {p['batch']}): {r['raw_text']}")
