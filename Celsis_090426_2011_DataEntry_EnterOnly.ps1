# Celsis Data Entry Automation — Enter-Only Mode
# Batch: 090426-2011 | Instrument: Advance 2 (ID: 2011) | Method: DI
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.
# Note: Automatically copies the appropriate control-group LIMS Note to clipboard for each sample.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "08/28/2026"
$EndDate   = "09/04/2026"
$GlobalATP = "88987"

$GSNote = @"
Day 7 Sterility Read: Negative. Incubation ended on 04Sep26

090426-2011: TSB -ve control = 2176 TSB cut off = 6526.5 FTM -ve control = 7334 FTM cut off = 22002.0
"@

$ESNote = @"
Day 7 Sterility Read: Negative. Incubation ended on 04Sep26

090426-2011: TSB -ve control = 2597 TSB cut off = 7791.0 FTM -ve control = 8089 FTM cut off = 24267.0
"@

$Playlist = @(
    [PSCustomObject]@{ ID="ETX-260825-0380"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="2612"; FTM="6383"; Group="GS"; Note=$GSNote },
    [PSCustomObject]@{ ID="ETX-260826-0689"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="2306"; FTM="5561"; Group="GS"; Note=$GSNote },
    [PSCustomObject]@{ ID="ETX-260826-0371"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="790";  FTM="2117"; Group="GS"; Note=$GSNote },
    [PSCustomObject]@{ ID="ETX-260826-0382"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="2649"; FTM="6761"; Group="GS"; Note=$GSNote },
    [PSCustomObject]@{ ID="ETX-260827-0684"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="2953"; FTM="5241"; Group="GS"; Note=$GSNote },
    [PSCustomObject]@{ ID="ETX-260826-0368"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="954";  FTM="2198"; Group="ES"; Note=$ESNote },
    [PSCustomObject]@{ ID="ETX-260826-0485"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="986";  FTM="3634"; Group="ES"; Note=$ESNote },
    [PSCustomObject]@{ ID="ETX-260826-0374"; Record="090426-2011"; Method="d"; ATP=$GlobalATP; TSB="983";  FTM="2870"; Group="ES"; Note=$ESNote }
)

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
Write-Host "  Celsis Data Entry — Batch 090426-2011 (8 samples)" -ForegroundColor Cyan
Write-Host "  ATP 88987 | GS: TSB 2176, FTM 7334 | ES: TSB 2597, FTM 8089" -ForegroundColor Cyan
Write-Host "  Mode: Enter-Only (Press ENTER to fill, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

for ($index = 0; $index -lt $Playlist.Count; $index++) {
    $Track = $Playlist[$index]

    Write-Host ""
    Write-Host ("[{0}/{1}] Next Sample: {2} (Group {3})" -f ($index + 1), $Playlist.Count, $Track.ID, $Track.Group) -ForegroundColor Yellow
    Write-Host "  Record=$($Track.Record) | Method=$($Track.Method) | ATP=$($Track.ATP) | TSB=$($Track.TSB) | FTM=$($Track.FTM)" -ForegroundColor Gray

    $command = Read-Host "Open ETX record, place cursor in Test Record box, and press [ENTER] (or Q to quit)"
    if ($command -match '^[Qq]$') {
        Write-Host "Stopped by user before $($Track.ID)." -ForegroundColor Red
        break
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

    Write-Host "[SUCCESS] $($Track.ID) populated!" -ForegroundColor Green
    Write-Host "[CLIPBOARD] Group $($Track.Group) Test Note copied to clipboard." -ForegroundColor Magenta
    Write-Host "--> Action: Verify fields, paste Note (Ctrl+V) into LIMS Note box, and Save manually." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Session finished. No automatic Save/Submit was performed." -ForegroundColor Cyan
explorer.exe /select,$PSScriptRoot\$MyInvocation.MyCommand.Name
