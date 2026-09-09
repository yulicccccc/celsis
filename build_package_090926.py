import os
import json
import zipfile
import pandas as pd

# Load final audit report
with open("celsis_090926_final_audit_report.json", "r", encoding="utf-8") as f:
    audit_data = json.load(f)

# 1. Generate Review Table TSV
df = pd.DataFrame(audit_data)
tsv_path = "Celsis_090926_Review_Table.tsv"
df.to_csv(tsv_path, sep="\t", index=False, encoding="utf-8")
print(f"1. Saved {tsv_path}")

# 2. Generate Bookmarklet Downloader HTML
# Create bookmarklet script that has buttons for each sample with color status
# Green for PASS & MATCH, Red for BLOCK
html_items = []
for idx, item in enumerate(audit_data, start=1):
    etx = item["Sample"]
    url = item["EagleTrax URL"]
    audit_res = item["Audit Result"]
    notes = item["Audit Notes"]
    tsb = item["PDF TSB"]
    ftm = item["PDF FTM"]
    cv = item["Max CV%"]
    
    is_blocked = "BLOCK" in audit_res
    bg_color = "#ffebee" if is_blocked else "#e8f5e9"
    border_color = "#c62828" if is_blocked else "#2e7d32"
    badge_color = "#c62828" if is_blocked else "#2e7d32"
    badge_text = "❌ BLOCK (CV≥30%)" if is_blocked else "✅ PASS (100% MATCH)"
    
    html_items.append(f"""
    <div class="sample-card" style="background: {bg_color}; border-left: 5px solid {border_color}; margin-bottom: 12px; padding: 12px; border-radius: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: bold; font-size: 16px;">#{idx}. <a href="{url}" target="_blank" style="color: #1565c0; text-decoration: none;">{etx}</a></span>
            <span style="background: {badge_color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{badge_text}</span>
        </div>
        <div style="margin-top: 6px; font-size: 13px; color: #37474f;">
            <strong>TSB:</strong> {tsb} | <strong>FTM:</strong> {ftm} | <strong>Max CV:</strong> {cv} | <strong>Notes:</strong> {notes}
        </div>
        <div style="margin-top: 6px;">
            <a href="{url}" target="_blank" class="btn-open" style="display: inline-block; background: #0288d1; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; text-decoration: none;">打开 EagleTrax 审核页 ↗</a>
        </div>
    </div>
    """)

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Celsis 090926 批次审签助手与书签器</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 25px; background: #f5f7fa; color: #263238; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #0d47a1; margin-top: 0; }}
        .summary-box {{ background: #e3f2fd; border-left: 4px solid #1976d2; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .btn-open:hover {{ background: #01579b !important; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🔬 Celsis 090926 批次审签助手 (39 样本)</h1>
    <div class="summary-box">
        <strong>质控审计状态：</strong><br>
        - 双仪器运行：Advance 2 (#2222, ATP 92047) 与 Advance 2 (#2011, ATP 95167)<br>
        - 38 个样本全部 100% 吻合（TSB/FTM/ATP/Modifications 均通过）<br>
        - <strong>1 个样本强制拦截：</strong> <span style="color: #c62828; font-weight: bold;">ETX-260901-0392</span> (Page 29, 第10容器 CV 33.2% ≥ 30%，触发 Rule 2 熔断)
    </div>
    <div class="list">
        {''.join(html_items)}
    </div>
</div>
</body>
</html>
"""

html_path = "090926_书签下载器.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print("2. Saved bookmarklet HTML")

# 3. Generate Enter-Only PowerShell script for 090926
# Only include whitelisted 38 samples
ps_tracks = []
for item in audit_data:
    if "BLOCK" in item["Audit Result"]:
        continue
    etx = item["Sample"]
    inst = item["Instrument"]
    atp = item["PDF ATP"]
    tsb = item["PDF TSB"]
    ftm = item["PDF FTM"]
    mod = item.get("LIMS Modification", "N/A")
    method = "m" if "Membrane" in str(item.get("LIMS Method", "")) else "d"
    rec = "090926-2222" if inst == "2222" else "090926-2011"
    
    ps_tracks.append(f'    [PSCustomObject]@{{ ID="{etx}"; Record="{rec}"; Method="{method}"; Mod="{mod}"; ATP="{atp}"; TSB="{tsb}"; FTM="{ftm}" }}')

ps_content = f"""# Celsis Data Entry Automation — Enter-Only Mode
# Batch: 090926-2222 & 090926-2011 | Samples: {len(ps_tracks)}
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "09/02/2026"
$EndDate   = "09/09/2026"

$Playlist = @(
{chr(10).join(ps_tracks)}
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
Write-Host "  Celsis Data Entry — Batch 090926 ({len(ps_tracks)} samples)" -ForegroundColor Cyan
Write-Host "  Mode: Enter-Only (Press ENTER to fill, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

for ($index = 0; $index -lt $Playlist.Count; $index++) {{
    $Track = $Playlist[$index]

    Write-Host ""
    Write-Host ("[{{0}}/{{1}}] Next Sample: {{2}}" -f ($index + 1), $Playlist.Count, $Track.ID) -ForegroundColor Yellow
    Write-Host "  Record=$($Track.Record) | Method=$($Track.Method) | ATP=$($Track.ATP) | TSB=$($Track.TSB) | FTM=$($Track.FTM)" -ForegroundColor Gray

    $command = Read-Host "Open ETX record, place cursor in Test Record box, and press [ENTER] (or Q to quit)"
    if ($command -match '^[Qq]$') {{
        Write-Host "Stopped by user before $($Track.ID)." -ForegroundColor Red
        break
    }}

    Write-Host "Starting in 2 seconds..." -ForegroundColor Red
    Start-Sleep -Seconds 1
    Write-Host "1..." -ForegroundColor Red
    Start-Sleep -Seconds 1

    # Form Sequence
    Send-ValueAndTab $Track.Record
    Send-ValueAndTab $Track.Method
    Send-ValueAndTab $Track.Mod 200

    # Skip 2 volume fields
    $WshShell.SendKeys("{{TAB}}")
    Start-Sleep -Milliseconds 150
    $WshShell.SendKeys("{{TAB}}")
    Start-Sleep -Milliseconds 150

    Send-ValueAndTab "ml"
    Send-ValueAndTab $StartDate
    Send-ValueAndTab $EndDate
    Send-ValueAndTab "y"
    Send-ValueAndTab $Track.ATP
    Send-ValueAndTab $Track.TSB
    Send-ValueAndTab $Track.FTM

    for ($i = 1; $i -le 4; $i++) {{
        Send-ValueAndTab "y" 150
    }}

    $WshShell.SendKeys("p")
    Write-Host "Populated $($Track.ID) successfully. Please verify and manually Save." -ForegroundColor Green
}}
"""

ps_path = "Celsis_090926_DataEntry_EnterOnly.ps1"
with open(ps_path, "w", encoding="utf-8") as f:
    f.write(ps_content)
print(f"3. Saved {ps_path}")

# 4. Bundle Complete Package ZIP
zip_path = "Celsis_090926_Complete_Package.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(tsv_path, os.path.basename(tsv_path))
    zf.write(html_path, os.path.basename(html_path))
    zf.write(ps_path, os.path.basename(ps_path))
    zf.write("celsis_090926_final_audit_report.json", "celsis_090926_final_audit_report.json")
    zf.write("celsis_090926_links_verified.json", "celsis_090926_links_verified.json")
print(f"4. Bundled {zip_path}")
