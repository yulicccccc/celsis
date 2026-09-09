import json
import re

with open('celsis_090926_step3_audit_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total samples audited: {len(data)}\n")
print(f"{'Sample':<16} | {'Method':<20} | {'Extracted Vol':<14} | {'Notes Summary'}")
print("-" * 80)

mf_count = 0
di_count = 0
unknown_count = 0

for s in data:
    method = s.get('LIMS Method', 'Unknown')
    notes = s.get('Extracted Notes', [])
    
    vol = "N/A"
    for n in notes:
        # Match e.g. 15ml, 12 mL, 50ml per media, 12.5ml
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:ml|mL)\s*(?:per media|of sample added)?', n, re.IGNORECASE)
        if m:
            vol = m.group(1) + " mL"
            break
            
    if "Membrane" in method:
        mf_count += 1
    elif "Direct" in method:
        di_count += 1
    else:
        unknown_count += 1

    summary_note = notes[1] if len(notes) > 1 else (notes[0] if notes else "")
    summary_note = summary_note.split("\t")[0][:45]
    print(f"{s['Sample']:<16} | {method:<20} | {vol:<14} | {summary_note}")

print("-" * 80)
print(f"Summary: MF (Membrane Filtration) = {mf_count} | DI (Direct Inoculation) = {di_count} | Unknown = {unknown_count}")
