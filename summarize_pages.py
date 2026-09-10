import os
import glob
import re

cache_dir = r"c:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\Celsis\ocr_cache_090926"
files = sorted(glob.glob(os.path.join(cache_dir, "page_*.txt")))

for f in files:
    page_name = os.path.basename(f)
    with open(f, "r", encoding="utf-8") as fp:
        text = fp.read()
    
    # Extract Workload Report
    wl_match = re.search(r"Workload Report:\s*([^\r\n]+)", text)
    wl = wl_match.group(1).strip() if wl_match else "UNKNOWN"
    
    # Extract Assay Name
    assay_match = re.search(r"Assay Name:\s*([^\r\n|]+)", text)
    assay = assay_match.group(1).strip() if assay_match else "UNKNOWN"
    
    # Extract Batch
    batch_match = re.search(r"Batch:\s*([A-Za-z0-9]+)", text)
    batch = batch_match.group(1).strip() if batch_match else ""
    
    # Extract Cutoffs
    neg_cut = re.search(r"Negative Cut-off:\s*([0-9.]+)", text)
    pos_cut = re.search(r"Positive Cut-off:\s*([0-9.]+)", text)
    cutoffs = f"Neg: {neg_cut.group(1) if neg_cut else 'N/A'}, Pos: {pos_cut.group(1) if pos_cut else 'N/A'}"
    
    # Find ETX patterns
    etx_list = re.findall(r"ETX[ -]?\d{6}[ -]?\d{4}(?:[- ][0-9]+)?", text)
    # Find Negative Control patterns (TSB, FTM, Reagent Blank, etc.)
    controls = re.findall(r"(?:TSB|FTM|Inst(?:rument)?\s*Bl(?:ank)?|Reag(?:ent)?\s*Bl(?:ank)?|ATP)\s*Control|Negative Control|Reagent Blank|Instrument Blank", text, re.IGNORECASE)
    
    print(f"[{page_name}] WL: {wl} | Batch: {batch} | Assay: {assay} | {cutoffs}")
    if controls:
        print(f"   Controls detected: {set(controls)}")
    if etx_list:
        print(f"   ETX samples ({len(etx_list)}): {etx_list[:5]} ... (total {len(etx_list)})")
    else:
        print("   No ETX samples found on this page.")
