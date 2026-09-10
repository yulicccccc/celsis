import json

with open('celsis_090926_final_audit_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

already_done = {
    'ETX-260830-0040', 
    'ETX-260830-0041', 
    'ETX-260827-0640', 
    'ETX-260831-0105', 
    'ETX-260831-0108', 
    'ETX-260831-0142', 
    'ETX-260831-0225'
}

unapproved = [s for s in report if 'PASS' in s.get('Audit Result', '') and s['Sample'] not in already_done]
print(f"Total remaining unapproved whitelisted: {len(unapproved)}")
print("\nNext 5 candidates for background approval:")
for idx, s in enumerate(unapproved[:5], 1):
    print(f"  {idx}. {s['Sample']} | Inst: #{s.get('Instrument')} | ATP: {s.get('PDF ATP')} | TSB: {s.get('PDF TSB')} | FTM: {s.get('PDF FTM')}")
