# Celsis Data Entry Automation — Enter-Only Mode
# Batch: 090926-2222 & 090926-2011 | Samples: 38
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "09/02/2026"
$EndDate   = "09/09/2026"

$Playlist = @(
    [PSCustomObject]@{ ID="ETX-260827-0640"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="645"; FTM="773" }
    [PSCustomObject]@{ ID="ETX-260830-0040"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2432"; FTM="8526" }
    [PSCustomObject]@{ ID="ETX-260830-0041"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2363"; FTM="6878" }
    [PSCustomObject]@{ ID="ETX-260831-0105"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="299"; FTM="309" }
    [PSCustomObject]@{ ID="ETX-260831-0108"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="3601"; FTM="4577" }
    [PSCustomObject]@{ ID="ETX-260831-0109"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="2852"; FTM="8329" }
    [PSCustomObject]@{ ID="ETX-260831-0142"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="3290"; FTM="7693" }
    [PSCustomObject]@{ ID="ETX-260831-0144"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="2737"; FTM="9391" }
    [PSCustomObject]@{ ID="ETX-260831-0204"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="256"; FTM="355" }
    [PSCustomObject]@{ ID="ETX-260831-0225"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="3176"; FTM="5788" }
    [PSCustomObject]@{ ID="ETX-260831-0310"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="595"; FTM="655" }
    [PSCustomObject]@{ ID="ETX-260831-0413"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="3076"; FTM="10107" }
    [PSCustomObject]@{ ID="ETX-260831-0564"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="3414"; FTM="7769" }
    [PSCustomObject]@{ ID="ETX-260831-0587"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2644"; FTM="7471" }
    [PSCustomObject]@{ ID="ETX-260831-0602"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2692"; FTM="8589" }
    [PSCustomObject]@{ ID="ETX-260831-0613"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2899"; FTM="8309" }
    [PSCustomObject]@{ ID="ETX-260831-0619"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2877"; FTM="6782" }
    [PSCustomObject]@{ ID="ETX-260831-0664"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="238"; FTM="313" }
    [PSCustomObject]@{ ID="ETX-260831-0673"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="3281"; FTM="8229" }
    [PSCustomObject]@{ ID="ETX-260831-0683"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="3514"; FTM="8232" }
    [PSCustomObject]@{ ID="ETX-260831-0694"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2806"; FTM="7940" }
    [PSCustomObject]@{ ID="ETX-260831-0837"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="3207"; FTM="7929" }
    [PSCustomObject]@{ ID="ETX-260901-0040"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="2670"; FTM="4540" }
    [PSCustomObject]@{ ID="ETX-260901-0046"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="2648"; FTM="4849" }
    [PSCustomObject]@{ ID="ETX-260901-0063"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="218"; FTM="490" }
    [PSCustomObject]@{ ID="ETX-260901-0229"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="258"; FTM="505" }
    [PSCustomObject]@{ ID="ETX-260901-0381"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="233"; FTM="474" }
    [PSCustomObject]@{ ID="ETX-260901-0385"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="1105"; FTM="2940" }
    [PSCustomObject]@{ ID="ETX-260901-0411"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="1201"; FTM="2664" }
    [PSCustomObject]@{ ID="ETX-260901-0428"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="251"; FTM="535" }
    [PSCustomObject]@{ ID="ETX-260901-0438"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="1429"; FTM="2215" }
    [PSCustomObject]@{ ID="ETX-260901-0478"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="2969"; FTM="7410" }
    [PSCustomObject]@{ ID="ETX-260901-0557"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="946"; FTM="2600" }
    [PSCustomObject]@{ ID="ETX-260901-0620"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="1425"; FTM="2726" }
    [PSCustomObject]@{ ID="ETX-260901-0639"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="286"; FTM="605" }
    [PSCustomObject]@{ ID="ETX-260901-0670"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="1270"; FTM="2634" }
    [PSCustomObject]@{ ID="ETX-260901-0692"; Record="090926-2222"; Method="d"; Mod="N/A"; ATP="92047"; TSB="229"; FTM="556" }
    [PSCustomObject]@{ ID="ETX-260902-0813"; Record="090926-2011"; Method="d"; Mod="N/A"; ATP="95167"; TSB="N/A"; FTM="2273" }
)

$WshShell = New-Object -ComObject WScript.Shell

function Send-ValueAndTab {
    param(
        [Parameter(Mandatory=$true)][string]$Value,
        [int]$DelayMs = 250
    )
    $WshShell.SendKeys($Value)
    $WshShell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds $DelayMs
}

Clear-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Celsis Data Entry — Batch 090926 (38 samples)" -ForegroundColor Cyan
Write-Host "  Mode: Enter-Only (Press ENTER to fill, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

for ($index = 0; $index -lt $Playlist.Count; $index++) {
    $Track = $Playlist[$index]

    Write-Host ""
    Write-Host ("[{0}/{1}] Next Sample: {2}" -f ($index + 1), $Playlist.Count, $Track.ID) -ForegroundColor Yellow
    Write-Host "  Record=$($Track.Record) | Method=$($Track.Method) | ATP=$($Track.ATP) | TSB=$($Track.TSB) | FTM=$($Track.FTM)" -ForegroundColor Gray

    $command = Read-Host "Open ETX record, place cursor in Test Record box, and press [ENTER] (or Q to quit)"
    if ($command -match '^[Qq]$') {
        Write-Host "Stopped by user before $($Track.ID)." -ForegroundColor Red
        break
    }

    Write-Host "Starting in 2 seconds..." -ForegroundColor Red
    Start-Sleep -Seconds 1
    Write-Host "1..." -ForegroundColor Red
    Start-Sleep -Seconds 1

    # Form Sequence
    Send-ValueAndTab $Track.Record
    Send-ValueAndTab $Track.Method
    Send-ValueAndTab $Track.Mod 200

    # Skip 2 volume fields
    $WshShell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds 150
    $WshShell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds 150

    Send-ValueAndTab "ml"
    Send-ValueAndTab $StartDate
    Send-ValueAndTab $EndDate
    Send-ValueAndTab "y"
    Send-ValueAndTab $Track.ATP
    Send-ValueAndTab $Track.TSB
    Send-ValueAndTab $Track.FTM

    for ($i = 1; $i -le 4; $i++) {
        Send-ValueAndTab "y" 150
    }

    $WshShell.SendKeys("p")
    Write-Host "Populated $($Track.ID) successfully. Please verify and manually Save." -ForegroundColor Green
}
