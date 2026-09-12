import json

rows = json.load(open('celsis_110926_all_rows_debug.json', 'r', encoding='utf-8'))
sids = ['0712', '0768', '0470', '0511', '0524', '0638', '0641', '0054', '0075', '0096']

for s in sids:
    print(f"\n=== Sample Ending in {s} ===")
    matches = [r for r in rows if s in r.get('text', '')]
    for m in matches:
        print(f"  Page {m['page']} ({m['media']}): {m['text']}")
