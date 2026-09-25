import json

with open('celsis_250926_final_audit_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

lines_md = [
    '| # | Sample | Instrument | Status | Method | Vol (F/A) | Note Vol | Daily ATP | Max TSB | Max FTM | Max CV% | PDF Pages | Result |',
    '|---|---|---|---|---|---|---|---|---|---|---|---|---|'
]

lines_tsv = [
    '#\tSample\tInstrument\tStatus\tMethod\tVol (F/A)\tNote Vol\tDaily ATP\tMax TSB\tMax FTM\tMax CV%\tPDF Pages\tResult\tEagleTrax URL'
]

for idx, r in enumerate(report, 1):
    sid = r['Sample']
    inst = r.get('Instrument', '')
    stat = r.get('LIMS Status', '')
    meth = 'MF' if 'Membrane' in r.get('LIMS Method', '') else ('DI' if 'Direct' in r.get('LIMS Method', '') else r.get('LIMS Method', ''))
    v_f = r.get('LIMS Filtered Volume', '')
    v_a = r.get('LIMS Added Volume', '')
    vol_str = f'F:{v_f}' if v_f else (f'A:{v_a}' if v_a else '-')
    n_vol = r.get('Canonical Note Volume') or '-'
    atp = r.get('LIMS ATP', '')
    tsb = r.get('LIMS TSB', '')
    ftm = r.get('LIMS FTM', '')
    cv_val = str(r.get('PDF Max CV%', '')).replace('%', '')
    cv = f"{cv_val}%" if cv_val else "-"
    pgs = ','.join(str(p) for p in r.get('PDF Pages', []))
    res = r.get('Audit Result', '')
    url = r.get('EagleTrax URL', '')

    link_md = f'[{sid}]({url})' if url else sid
    res_md = '✅ PASS' if res == 'PASS' else f'❌ {res}'
    lines_md.append(f'| {idx} | {link_md} | {inst} | {stat} | {meth} | {vol_str} | {n_vol} | {atp} | {tsb} | {ftm} | {cv} | {pgs} | {res_md} |')
    lines_tsv.append(f'{idx}\t{sid}\t{inst}\t{stat}\t{meth}\t{vol_str}\t{n_vol}\t{atp}\t{tsb}\t{ftm}\t{cv}\t{pgs}\t{res}\t{url}')

with open('celsis_250926_final_audit_table.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines_md))

with open('celsis_250926_final_audit_table.tsv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines_tsv))

print(f'Exported {len(report)} rows to celsis_250926_final_audit_table.md and .tsv')
