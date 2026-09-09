# Celsis Data Entry Automation — Single Sample Mode
# Sample: ETX-260826-0374 | Batch: 090426-2011 | Instrument: Advance 2 (ID: 2011) | Method: DI
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.
# Note: Automatically copies the ES control-group LIMS Note to clipboard.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "08/28/2026"
$EndDate   = "09/04/2026"
$GlobalATP = "88987"

$ESNote = @"
Day 7 Sterility Read: Negative. Incubation ended on 04Sep26

090426-2011: TSB -ve control = 2597 TSB cut off = 7791.0 FTM -ve control = 8089 FTM cut off = 24267.0
"@

$Track = [PSCustomObject]@{
    ID     = "ETX-260826-0374"
    Record = "090426-2011"
    Method = "d"
    ATP    = $GlobalATP
    TSB    = "983"
    FTM    = "2870"
    Group  = "ES"
    Note   = $ESNote
}

$WshShell = New-Object -ComObject WScript.Shell

function Send-ValueAndTab {
    param(
        [Parameter(Mandatory=$true)][string]$Value,
        [int]$DelayMs = 300
    )
    $WshShell.SendKeys($Value)
    $WshShell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds $DelayMs
}

Clear-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Celsis Data Entry — ONLY for $($Track.ID)" -ForegroundColor Cyan
Write-Host "  Batch: 090426-2011 | Group: ES" -ForegroundColor Cyan
Write-Host "  ATP: 88987 | TSB: 983 | FTM: 2870" -ForegroundColor Cyan
Write-Host "  Mode: Enter-Only (Press ENTER to fill, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target Sample: $($Track.ID)" -ForegroundColor Yellow
Write-Host "  Record=$($Track.Record) | Method=$($Track.Method) | ATP=$($Track.ATP) | TSB=$($Track.TSB) | FTM=$($Track.FTM)" -ForegroundColor Gray
Write-Host ""

$command = Read-Host "Open ETX-260826-0374 in EagleTrax, place cursor in Test Record box, and press [ENTER] (or Q to quit)"
if ($command -match '^[Qq]$') {
    Write-Host "Cancelled by user." -ForegroundColor Red
    exit
}

Write-Host "Starting in 3 seconds..." -ForegroundColor Red
Start-Sleep -Seconds 1
Write-Host "2..." -ForegroundColor Red
Start-Sleep -Seconds 1
Write-Host "1..." -ForegroundColor Red
Start-Sleep -Seconds 1

# EagleTrax Form Sequence
Send-ValueAndTab $Track.Record
Send-ValueAndTab $Track.Method
Send-ValueAndTab "N/A" 200

# Skip 2 fields after N/A
$WshShell.SendKeys("{TAB}")
Start-Sleep -Milliseconds 200
$WshShell.SendKeys("{TAB}")
Start-Sleep -Milliseconds 200

Send-ValueAndTab "ml"
Send-ValueAndTab $StartDate
Send-ValueAndTab $EndDate
Send-ValueAndTab "y"
Send-ValueAndTab $Track.ATP
Send-ValueAndTab $Track.TSB
Send-ValueAndTab $Track.FTM

# 4 Yes/No fields
for ($i = 1; $i -le 4; $i++) {
    Send-ValueAndTab "y" 200
}

# Result 'p' (Pass)
$WshShell.SendKeys("p")
Start-Sleep -Milliseconds 300

# Copy LIMS Note to Clipboard
Set-Clipboard -Value $Track.Note

Write-Host ""
Write-Host "[SUCCESS] $($Track.ID) populated!" -ForegroundColor Green
Write-Host "[CLIPBOARD] Group ES Test Note copied to clipboard." -ForegroundColor Magenta
Write-Host "--> Action: Verify fields, paste Note (Ctrl+V) into LIMS Note box, and Save manually." -ForegroundColor Cyan
Write-Host ""
Write-Host "Done. No automatic Save/Submit was performed." -ForegroundColor Cyan
explorer.exe /select,$PSScriptRoot\$MyInvocation.MyCommand.Name
