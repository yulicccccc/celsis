import json
import re

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

parsed_records = []

for p in pages:
    page_num = p["page_num"]
    wl = p["wl_name"]
    batch = p["batch"]
    page_of = p["page_of"]
    rows = p["rows"]
    
    # Check if cutoff is in header or in rows
    cutoff = p.get("neg_cutoff")
    current_media = "UNKNOWN"
    
    for r in rows:
        text = r["raw_text"]
        
        # Check for cutoff row
        cut_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", text, re.I)
        if cut_m:
            cutoff = float(cut_m.group(1))
            
        # Check for media/control row
        # e.g., TSB,MF,-ve control or FTM,MF,-ve control or TSB,DI or FTM,DI
        if "control" in text.lower() or "cal ok" in text.lower():
            media_type = "UNKNOWN"
            if "tsb" in text.lower():
                media_type = "TSB"
            elif "ftm" in text.lower():
                media_type = "FTM"
            elif "reagent" in text.lower():
                media_type = "Reagent Blank"
            elif "inst" in text.lower():
                media_type = "Inst Blank"
            elif "atp" in text.lower():
                media_type = "ATP Positive"
                
            parsed_records.append({
                "page": page_num,
                "type": "CONTROL",
                "media": media_type,
                "raw": text,
                "cutoff": cutoff,
                "wl": wl,
                "batch": batch
            })
            if media_type in ["TSB", "FTM"]:
                current_media = media_type

        # Check for sample row (ETX)
        # Regex to match ETX-YYMMDD-XXXX
        etx_m = re.search(r"(ETX[ -]?[0-9]{6}[ -]?[0-9]{4}(?:[- /0-9]+)?)", text)
        if etx_m:
            raw_etx = etx_m.group(1).strip()
            # clean etx
            clean_m = re.search(r"(ETX[ -]?[0-9]{6}[ -]?[0-9]{4})", raw_etx)
            clean_etx = clean_m.group(1).replace(" ", "-") if clean_m else raw_etx
            
            parsed_records.append({
                "page": page_num,
                "type": "SAMPLE",
                "media": current_media,
                "raw_etx": raw_etx,
                "etx": clean_etx,
                "raw": text,
                "cutoff": cutoff,
                "wl": wl,
                "batch": batch
            })

print(f"Total parsed records: {len(parsed_records)}")
samples = [r for r in parsed_records if r["type"] == "SAMPLE"]
controls = [r for r in parsed_records if r["type"] == "CONTROL"]
print(f"Controls: {len(controls)}, Samples: {len(samples)}")

unique_etx = sorted(list(set(s["etx"] for s in samples)))
print(f"Unique ETX count: {len(unique_etx)}")
for u in unique_etx:
    s_entries = [s for s in samples if s["etx"] == u]
    pages_found = sorted(list(set(s["page"] for s in s_entries)))
    print(f"  {u}: {len(s_entries)} entries on pages {pages_found}")
