import json

with open('celsis_220926_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
with open('celsis_220926_links.json', 'r', encoding='utf-8') as f:
    links = json.load(f)

link_samples = set(item['Sample'] for item in links)
missing = [item for item in db if item['Sample'] not in link_samples]

print(f"Total missing from user links: {len(missing)}")
for m in missing:
    sid = m['Sample']
    inst = m['Instrument']
    pgs = m['Pages']
    atp = m['Daily ATP']
    tsb = m['Max TSB RLU']
    ftm = m['Max FTM RLU']
    cv = m['Max CV%']
    print(f"| {sid} | {inst} | {atp} | {tsb} | {ftm} | {cv}% | Pages {pgs} |")
