import json

rows = json.load(open('celsis_110926_all_rows_debug.json', 'r', encoding='utf-8'))
targets = ['0079', '0088', '0386', '0789', '0631']

for t in targets:
    print(f"\n=== Target: {t} ===")
    matches = [r for r in rows if t in r.get('text', '')]
    for m in matches:
        print(f"  Page {m['page']} ({m['media']}): {m['text']}")
