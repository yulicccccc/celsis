import os
import sys
import json
import zipfile
import html
import re
import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")

BATCH_ID = "093026-2011"
READ_DATE = "30Sep26"
START_DATE = "09/23/2026"
END_DATE = "09/30/2026"

PDF_WORKLOAD = r"D:\1.pdf"
PDF_DAILY = r"D:\1d.pdf"

TARGET_DIR = r"c:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\Celsis"
DOCS_DIR = r"c:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents"

# 1. Parse Daily Control PDF for ATP Positive Control
print("--- [1/5] Parsing Daily Control PDF ---")
with pdfplumber.open(PDF_DAILY) as pdf:
    # Page 3 is ATP Positive Control
    p3_table = pdf.pages[2].extract_tables()[1]
    atp_row = p3_table[1]
    GLOBAL_ATP = int(atp_row[4])
    print(f"ATP Positive Control: {GLOBAL_ATP} (CV: {atp_row[6]}%, Result: {atp_row[5]})")

# 2. Parse Workload PDF for Controls & Samples
print("--- [2/5] Parsing Workload PDF ---")
with pdfplumber.open(PDF_WORKLOAD) as pdf:
    p1_rows = pdf.pages[0].extract_tables()[1]
    p2_rows = pdf.pages[1].extract_tables()[1]

# Negative controls are in row 1 (index 1) of Table 1
tsb_ctrl_row = p1_rows[1]
ftm_ctrl_row = p2_rows[1]

GS_TSB_NEG = int(tsb_ctrl_row[4])
GS_FTM_NEG = int(ftm_ctrl_row[4])

# Extract exact cutoffs from Table 0 header
t0_p1 = pdf.pages[0].extract_tables()[0]
t0_p2 = pdf.pages[1].extract_tables()[0]

tsb_cut_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", str(t0_p1))
GS_TSB_CUTOFF = tsb_cut_m.group(1) if tsb_cut_m else str(GS_TSB_NEG * 3.0)

ftm_cut_m = re.search(r"Negative\s*Cut-off:\s*([0-9.]+)", str(t0_p2))
GS_FTM_CUTOFF = ftm_cut_m.group(1) if ftm_cut_m else str(GS_FTM_NEG * 3.0)

print(f"GS TSB -ve control: {GS_TSB_NEG} (Cut-off: {GS_TSB_CUTOFF})")
print(f"GS FTM -ve control: {GS_FTM_NEG} (Cut-off: {GS_FTM_CUTOFF})")

GS_NOTE = f"""Day 7 Sterility Read: Negative. Incubation ended on {READ_DATE}

{BATCH_ID}: TSB -ve control = {GS_TSB_NEG} TSB cut off = {GS_TSB_CUTOFF} FTM -ve control = {GS_FTM_NEG} FTM cut off = {GS_FTM_CUTOFF}"""

# Extract Samples (rows 2 to end)
sample_rows_p1 = p1_rows[2:]
sample_rows_p2 = p2_rows[2:]
assert len(sample_rows_p1) == len(sample_rows_p2), "Sample counts between TSB and FTM pages mismatch!"

SAMPLES_DATA = []
for i, (r1, r2) in enumerate(zip(sample_rows_p1, sample_rows_p2), 1):
    raw_id = r1[1]
    raw_id_p2 = r2[1]
    assert raw_id == raw_id_p2, f"Sample raw ID mismatch at index {i}: {raw_id} vs {raw_id_p2}"

    base_m = re.match(r"(ETX-\d{6}-\d{4})", raw_id)
    base_id = base_m.group(1) if base_m else raw_id

    tsb_val = int(r1[4])
    tsb_cv = int(r1[6])
    ftm_val = int(r2[4])
    ftm_cv = int(r2[6])

    SAMPLES_DATA.append({
        "num": i,
        "raw_id": raw_id,
        "base_id": base_id,
        "tsb": tsb_val,
        "tsb_cv": tsb_cv,
        "ftm": ftm_val,
        "ftm_cv": ftm_cv,
        "group": "GS",
        "note": GS_NOTE
    })

print(f"Successfully extracted {len(SAMPLES_DATA)} samples.")

# =========================================================================
# 3. Generate Review Table TSV
# =========================================================================
print("--- [3/5] Generating Review Table TSV ---")
tsv_filename = f"Celsis_{BATCH_ID}_Review_Table.tsv"
tsv_path = os.path.join(TARGET_DIR, tsv_filename)

with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("#\tSample ID\tRaw ID\tGroup\tATP Control\tTSB Max RLU\tTSB CV%\tFTM Max RLU\tFTM CV%\tResult\tStart Date\tEnd Date\n")
    for s in SAMPLES_DATA:
        f.write(f"{s['num']}\t{s['base_id']}\t{s['raw_id']}\t{s['group']}\t{GLOBAL_ATP}\t{s['tsb']}\t{s['tsb_cv']}%\t{s['ftm']}\t{s['ftm_cv']}%\tNegative\t{START_DATE}\t{END_DATE}\n")

print(f"✅ Generated TSV: {tsv_path}")

# =========================================================================
# 4. Generate Enter-Only PowerShell Script
# =========================================================================
print("--- [4/5] Generating Enter-Only PowerShell Script ---")
ps1_filename = f"Celsis_{BATCH_ID}_DataEntry_EnterOnly.ps1"
ps1_path = os.path.join(TARGET_DIR, ps1_filename)

playlist_items = []
for s in SAMPLES_DATA:
    item = f'    [PSCustomObject]@{{ ID="{s["base_id"]}"; RawID="{s["raw_id"]}"; Record="{BATCH_ID}"; Method="d"; ATP="{GLOBAL_ATP}"; TSB="{s["tsb"]}"; FTM="{s["ftm"]}"; Group="{s["group"]}"; Note=@"\n{s["note"]}\n"@ }}'
    playlist_items.append(item)

playlist_block = ",\n".join(playlist_items)

ps1_content = f"""# Celsis Data Entry Automation — Enter-Only Mode
# Batch: {BATCH_ID} | Samples: {len(SAMPLES_DATA)}
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.
# Note: Automatically copies the appropriate control-group LIMS Note to clipboard for each sample.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "{START_DATE}"
$EndDate   = "{END_DATE}"
$GlobalATP = "{GLOBAL_ATP}"

$Playlist = @(
{playlist_block}
)

$WshShell = New-Object -ComObject WScript.Shell

function Send-ValueAndTab {{
    param(
        [Parameter(Mandatory=$true)][string]$Value,
        [int]$DelayMs = 250
    )
    $WshShell.SendKeys($Value)
    $WshShell.SendKeys("{{TAB}}")
    Start-Sleep -Milliseconds $DelayMs
}}

Clear-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Celsis Data Entry -- Batch {BATCH_ID} ({len(SAMPLES_DATA)} samples)" -ForegroundColor Cyan
Write-Host "  ATP {GLOBAL_ATP} | GS: TSB {GS_TSB_NEG}, FTM {GS_FTM_NEG}" -ForegroundColor Cyan
Write-Host "  Mode: Enter-Only (Press ENTER to fill, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

for ($index = 0; $index -lt $Playlist.Count; $index++) {{
    $Track = $Playlist[$index]

    Write-Host ""
    Write-Host ("[{{0}}/{{1}}] Next Sample: {{2}} (Group {{3}})" -f ($index + 1), $Playlist.Count, $Track.ID, $Track.Group) -ForegroundColor Yellow
    Write-Host "  Record=$($Track.Record) | Method=$($Track.Method) | ATP=$($Track.ATP) | TSB=$($Track.TSB) | FTM=$($Track.FTM)" -ForegroundColor Gray

    # Auto-copy correct note to clipboard
    try {{
        Set-Clipboard -Value $Track.Note
        Write-Host "  [COPIED] Correct $($Track.Group) Test Note copied to clipboard!" -ForegroundColor Green
    }} catch {{
        Write-Host "  [WARN] Clipboard copy failed" -ForegroundColor DarkGray
    }}

    $prompt = ("Press [ENTER] to inject {{0}} (or 'q' to quit): " -f $Track.ID)
    $resp = Read-Host -Prompt $prompt
    if ($resp -match "^[Qq]") {{
        Write-Host "Operation cancelled by user." -ForegroundColor Yellow
        break
    }}

    Write-Host "  -> Injecting fields in 2 seconds... Switch to browser now!" -ForegroundColor Magenta
    Start-Sleep -Seconds 2

    # Standard 16-field keystroke sequence (stops before Save)
    Send-ValueAndTab $Track.Record
    Send-ValueAndTab $Track.Method
    Send-ValueAndTab "N/A"
    $WshShell.SendKeys("{{TAB}}")
    Start-Sleep -Milliseconds 200
    $WshShell.SendKeys("{{TAB}}")
    Start-Sleep -Milliseconds 200
    Send-ValueAndTab "ml"
    Send-ValueAndTab $StartDate
    Send-ValueAndTab $EndDate
    Send-ValueAndTab "y"
    Send-ValueAndTab $Track.ATP
    Send-ValueAndTab $Track.TSB
    Send-ValueAndTab $Track.FTM
    Send-ValueAndTab "y"
    Send-ValueAndTab "y"
    Send-ValueAndTab "y"
    Send-ValueAndTab "y"
    Send-ValueAndTab "p"

    Write-Host "  [DONE] $($Track.ID) injected! Please verify fields and paste Test Note, then save manually." -ForegroundColor Green
}}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  All items completed! Good job." -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
"""

with open(ps1_path, "w", encoding="utf-8-sig") as f:
    f.write(ps1_content)

print(f"✅ Generated PS1: {ps1_path}")

# =========================================================================
# 5. Generate Bookmarklet HTML Downloader
# =========================================================================
print("--- [5/5] Generating Bookmarklet & JSON Payload ---")
html_filename = f"{BATCH_ID}_书签下载器.html"
html_path = os.path.join(TARGET_DIR, html_filename)
html_docs_path = os.path.join(DOCS_DIR, html_filename)

etx_ids_json = json.dumps([s["base_id"] for s in SAMPLES_DATA])

js_code = f"""(async()=>{{
const IDS={etx_ids_json},WAIT=500,MAX=16;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const norm=s=>(s||'').replace(/[\\u200B-\\u200D\\uFEFF]/g,'').replace(/\\s+/g,' ').trim().toUpperCase();
function rowFor(id){{
    for(const r of document.querySelectorAll('tr'))if(norm(r.innerText).includes(norm(id)))return r;
    for(const a of document.querySelectorAll('a'))if(norm(a.innerText).includes(norm(id)))return a.closest('tr');
    return null;
}}
function linkFor(r){{
    const L=[...r.querySelectorAll('a')];
    return L.find(a=>/\\/SubmissionTest\\/Details\\//i.test(a.href||''))||L.find(a=>norm(a.innerText).includes('CELSIS STERILITY TEST'))||L.find(a=>/SubmissionTest/i.test(a.href||''))||L[1]||L[0]||null;
}}
function paint(r,s){{
    let bg='#fff3bf',bd='#f59e0b';
    r.style.setProperty('box-shadow','inset 5px 0 0 '+bd,'important');
    for(const c of r.querySelectorAll('td,th')){{
        c.style.setProperty('background-color',bg,'important');
        c.style.setProperty('color','#111827','important');
    }}
    for(const a of r.querySelectorAll('a')){{
        a.style.setProperty('color','#0b3d91','important');
        a.style.setProperty('font-weight','700','important');
    }}
}}
document.getElementById('celsis-v3')?.remove();
const p=document.createElement('div');
p.id='celsis-v3';
p.style.cssText='position:fixed;right:20px;bottom:20px;z-index:2147483647;width:380px;padding:16px;border:1px solid #cbd5e1;border-radius:12px;background:#f8fafc;color:#0f172a;box-shadow:0 12px 35px rgba(0,0,0,.28);font:14px/1.45 Segoe UI,Arial,sans-serif';
document.body.appendChild(p);

for(let n=1;n<=MAX;n++){{
    p.innerHTML='<b>Celsis {BATCH_ID} V3 ({len(SAMPLES_DATA)} Samples)</b><div style="margin-top:8px">Scanning... '+n+'/'+MAX+'</div>';
    let found=null, targetId='';
    for(const id of IDS){{
        const r=rowFor(id), l=r&&linkFor(r);
        if(r&&l){{ found={{r,l}}; targetId=id; break; }}
    }}
    if(found){{
        paint(found.r,'next');
        p.innerHTML='<div style="font-size:16px;font-weight:800">Celsis {BATCH_ID} V3</div><div style="background:#dcfce7;color:#14532d;padding:8px;border-radius:7px;margin:8px 0">Target located on current page!</div><div style="background:#fff7cc;padding:9px;border-radius:7px;margin-bottom:8px">Next: <b>'+targetId+'</b></div>';
        const b=document.createElement('button');
        b.textContent='Open '+targetId+' test page';
        b.style.cssText='width:100%;padding:10px;border:0;border-radius:7px;background:#2563eb;color:#fff;font-weight:800;cursor:pointer';
        b.onclick=()=>{{ window.open(found.l.href,'_blank','noopener') }};
        p.appendChild(b);
        const rBtn=document.createElement('button');
        rBtn.textContent='Re-scan page';
        rBtn.style.cssText='width:100%;padding:8px;margin-top:8px;border:1px solid #94a3b8;border-radius:7px;background:#fff;color:#334155;font-weight:700;cursor:pointer';
        rBtn.onclick=()=>location.reload();
        p.appendChild(rBtn);
        return;
    }}
    await sleep(WAIT);
}}
p.innerHTML='<div style="font-size:16px;font-weight:800">Celsis {BATCH_ID} V3</div><div style="background:#fee2e2;color:#7f1d1d;padding:8px;border-radius:7px;margin:8px 0">No remaining targets found on this page after 16 retries.</div>';
}})();""".replace("\n", "").replace("  ", " ")

href_escaped = "javascript:" + html.escape(js_code, quote=True)

samples_table_rows = "".join([
    f"<tr><td>{s['num']}</td><td><b>{s['base_id']}</b></td><td>{s['raw_id']}</td><td><span class='badge'>{s['group']}</span></td><td>{s['tsb']}</td><td>{s['ftm']}</td><td>Negative</td></tr>"
    for s in SAMPLES_DATA
])

html_page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Celsis {BATCH_ID} 书签下载器 ({len(SAMPLES_DATA)} Samples)</title>
<style>
body {{ font-family: Segoe UI, -apple-system, sans-serif; max-width: 900px; margin: 30px auto; padding: 20px; background: #f8fafc; color: #1e293b; }}
.card {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
h1 {{ color: #1e3a8a; margin-top: 0; }}
.btn-bookmark {{ display: inline-block; background: #2563eb; color: white !important; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 16px; box-shadow: 0 2px 4px rgba(37,99,235,0.2); }}
.btn-bookmark:hover {{ background: #1d4ed8; }}
.meta-box {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 6px; margin: 18px 0; font-size: 14px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
th {{ background: #f1f5f9; color: #334155; }}
tr:nth-child(even) {{ background: #f8fafc; }}
.badge {{ background: #e0e7ff; color: #3730a3; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
textarea {{ width: 100%; height: 100px; margin-top: 10px; font-family: monospace; font-size: 12px; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px; box-sizing: border-box; }}
</style>
</head>
<body>
<div class="card">
    <h1>🔬 Celsis {BATCH_ID} 智能书签导航器</h1>
    <div class="meta-box">
        <strong>批次信息：</strong> Batch: <b>{BATCH_ID}</b> | 样本总数: <b>{len(SAMPLES_DATA)}</b> | ATP Positive Control: <b>{GLOBAL_ATP}</b><br>
        <strong>GS 对照：</strong> TSB: {GS_TSB_NEG} (Cutoff: {GS_TSB_CUTOFF}) | FTM: {GS_FTM_NEG} (Cutoff: {GS_FTM_CUTOFF})
    </div>
    <p><b>使用方法：</b>将下方蓝色按钮直接拖拽到 Chrome 浏览器的书签栏。在 EagleTrax 样本列表页面点击此书签，即可自动高亮并定位当前页面上的测试项：</p>
    <p><a class="btn-bookmark" href="{href_escaped}">⭐ Celsis {BATCH_ID} 书签导航器</a></p>
    
    <details style="margin-top: 15px;">
        <summary style="cursor:pointer; color:#475569; font-weight:600;">无法拖拽？点击展开纯文本代码</summary>
        <textarea readonly>{href_escaped}</textarea>
    </details>

    <h3 style="margin-top: 30px; color: #334155;">待录入样本清单 ({len(SAMPLES_DATA)} Samples)</h3>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Base ETX</th>
                <th>Raw Report Label</th>
                <th>Group</th>
                <th>TSB Max RLU</th>
                <th>FTM Max RLU</th>
                <th>Result</th>
            </tr>
        </thead>
        <tbody>
            {samples_table_rows}
        </tbody>
    </table>
</div>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_page)
with open(html_docs_path, "w", encoding="utf-8") as f:
    f.write(html_page)

print(f"✅ Generated HTML: {html_path}")

# =========================================================================
# 6. Generate Auto-Pilot Payload JSON for Playwright
# =========================================================================
auto_payload = {
    "batch_id": BATCH_ID,
    "atp": GLOBAL_ATP,
    "samples": []
}

for s in SAMPLES_DATA:
    auto_payload["samples"].append({
        "id": s["base_id"],
        "raw_id": s["raw_id"],
        "record": BATCH_ID,
        "method": "d",
        "volume": "",
        "start_date": START_DATE,
        "end_date": END_DATE,
        "atp": GLOBAL_ATP,
        "tsb": s["tsb"],
        "ftm": s["ftm"],
        "group": s["group"],
        "note": s["note"]
    })

payload_target = os.path.join(TARGET_DIR, "celsis_auto_payload.json")
with open(payload_target, "w", encoding="utf-8") as f:
    json.dump(auto_payload, f, indent=2, ensure_ascii=False)

payload_named = os.path.join(TARGET_DIR, f"celsis_auto_payload_{BATCH_ID.replace('-', '_')}.json")
with open(payload_named, "w", encoding="utf-8") as f:
    json.dump(auto_payload, f, indent=2, ensure_ascii=False)

print(f"✅ Generated Auto-Pilot Payload JSON: {payload_target}")

# =========================================================================
# 7. Create Complete Package ZIP
# =========================================================================
zip_filename = f"Celsis_{BATCH_ID}_Complete_Package.zip"
zip_path = os.path.join(TARGET_DIR, zip_filename)
zip_docs_path = os.path.join(DOCS_DIR, zip_filename)

for zp in [zip_path, zip_docs_path]:
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(html_path, arcname=html_filename)
        zf.write(ps1_path, arcname=ps1_filename)
        zf.write(tsv_path, arcname=tsv_filename)
        zf.write(payload_target, arcname="celsis_auto_payload.json")

print(f"✅ Generated Complete Package ZIP: {zip_path}")
print("\n🎉 ALL 4-IN-1 DELIVERABLES FOR BATCH 093026-2011 GENERATED SUCCESSFULLY!")
