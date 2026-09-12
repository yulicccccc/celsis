import json
import re

with open("celsis_100926_pages_raw.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} pages from celsis_100926_pages_raw.json")

print("\n=== 1. DAILY CONTROLS ===")
for p in pages:
    if p["is_daily"]:
        pno = p["page_num"]
        wl = p["wl_name"]
        tbl = p["table_text"]
        print(f"Page {pno:02d}: WL='{wl}'")
        for line in tbl.splitlines():
            l = line.strip()
            if any(k in l.lower() for k in ["atp", "pos", "control", "reagent", "blank", "cal ok"]):
                print(f"   {l}")

print("\n=== 2. WORKLOAD OVERVIEW ===")
for p in pages:
    if not p["is_daily"]:
        pno = p["page_num"]
        wl = p["wl_name"]
        b = p["batch"]
        print(f"Page {pno:02d}: WL='{wl}' | Batch={b} | Cutoff={p.get('neg_cutoff')}")

print("\n=== 3. SAMPLES DETECTED ===")
all_etx = {}
for p in pages:
    if not p["is_daily"]:
        pno = p["page_num"]
        wl = p["wl_name"]
        tbl = p["table_text"]
        # search for ETX
        matches = re.findall(r"(ETX[ -]?[0-9]{6}[ -]?[0-9]{4})", tbl)
        for m in matches:
            norm = m.replace(" ", "-")
            if norm not in all_etx:
                all_etx[norm] = []
            all_etx[norm].append((pno, wl))

print(f"Total Unique ETX detected in raw text: {len(all_etx)}")
for k in sorted(all_etx.keys()):
    pages_list = sorted(list(set(x[0] for x in all_etx[k])))
    wls = sorted(list(set(x[1] for x in all_etx[k])))
    print(f"  {k}: found {len(all_etx[k])} times on pages {pages_list} (WL: {wls})")
