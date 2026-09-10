import json

report = json.load(open('celsis_100926_final_audit_report.json', 'r', encoding='utf-8'))
blocked = [r for r in report if 'BLOCK' in r.get('Audit Result', '')]
print(f'Total blocked: {len(blocked)}')
for idx, b in enumerate(blocked, 1):
    print(f"[{idx:02d}] {b['Sample']}")
    print(f"     LIMS: Method={b.get('LIMS Method')}, FiltVol={b.get('LIMS Filtered Volume')}, AddedVol={b.get('LIMS Added Volume')}")
    print(f"     LIMS RLU: ATP={b.get('LIMS ATP')}, TSB={b.get('LIMS TSB')}, FTM={b.get('LIMS FTM')}")
    print(f"     PDF  RLU: ATP={b.get('PDF ATP')}, TSB={b.get('PDF TSB')}, FTM={b.get('PDF FTM')}")
    print(f"     Discrepancies: {b.get('Discrepancies')}")
