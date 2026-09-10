import json
import re

rows = json.load(open('celsis_100926_all_rows_debug.json', 'r', encoding='utf-8'))
targets = ['0137', '0155', '0192', '0195', '0202', '0216', '0207', '0141', '0517', '0632']

print("Searching debug rows for targets:")
for t in targets:
    print(f"\n=== Target: {t} ===")
    matches = [r for r in rows if t in r.get('text', '')]
    for m in matches:
        print(f"  Page {m['page']} ({m['media']}): {m['text']}")
