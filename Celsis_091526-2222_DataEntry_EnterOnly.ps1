# Celsis Data Entry Automation — Enter-Only Mode
# Batch: 091526-2222 | Samples: 34
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.
# Note: Automatically copies the appropriate control-group LIMS Note to clipboard for each sample.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "09/08/2026"
$EndDate   = "09/15/2026"
$GlobalATP = "87468"

$Playlist = @(
    [PSCustomObject]@{ ID="ETX-260903-0229"; RawID="ETX-260903-0229-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="1980"; FTM="6423"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0227"; RawID="ETX-260903-0227-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2997"; FTM="6213"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0291"; RawID="ETX-260902-0291-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2239"; FTM="8700"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0295"; RawID="ETX-260902-0295-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2541"; FTM="9084"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0287"; RawID="ETX-260902-0287-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2534"; FTM="6626"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0289"; RawID="ETX-260902-0289-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2233"; FTM="6233"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0228"; RawID="ETX-260903-0228-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2221"; FTM="7205"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0564"; RawID="ETX-260903-0564-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2403"; FTM="6645"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0578"; RawID="ETX-260903-0578-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2279"; FTM="7106"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0793"; RawID="ETX-260903-0793-6/7"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2594"; FTM="8546"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0226"; RawID="ETX-260903-0226-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2480"; FTM="8593"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0294"; RawID="ETX-260902-0294-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2348"; FTM="8769"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0774"; RawID="ETX-260903-0774-6/7"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2243"; FTM="8442"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0566"; RawID="ETX-260903-0566-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2479"; FTM="6278"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0221"; RawID="ETX-260903-0221-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2398"; FTM="7259"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0285"; RawID="ETX-260902-0285-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2617"; FTM="6234"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0234"; RawID="ETX-260903-0234-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2405"; FTM="6343"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0222"; RawID="ETX-260903-0222-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2357"; FTM="7210"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0279"; RawID="ETX-260902-0279-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2323"; FTM="6226"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0292"; RawID="ETX-260902-0292-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2681"; FTM="6611"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0225"; RawID="ETX-260903-0225-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2696"; FTM="7066"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0282"; RawID="ETX-260902-0282-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2282"; FTM="8203"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0236"; RawID="ETX-260903-0236-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2625"; FTM="6455"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0231"; RawID="ETX-260903-0231-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2487"; FTM="6766"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0290"; RawID="ETX-260902-0290-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2519"; FTM="6638"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0276"; RawID="ETX-260902-0276-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2612"; FTM="6426"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0283"; RawID="ETX-260902-0283-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2597"; FTM="6536"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260902-0269"; RawID="ETX-260902-0269-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2668"; FTM="6526"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260903-0219"; RawID="ETX-260903-0219-4/6"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2751"; FTM="6028"; Group="GS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5
"@ },
    [PSCustomObject]@{ ID="ETX-260904-0486"; RawID="ETX-260904-0486-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2898"; FTM="6382"; Group="GS+PBS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2734 TSB cut off = 8202.0 FTM -ve control = 6054 FTM cut off = 18162.0
"@ },
    [PSCustomObject]@{ ID="ETX-260904-0451"; RawID="ETX-260904-0451-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2332"; FTM="7722"; Group="GS+PBS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2734 TSB cut off = 8202.0 FTM -ve control = 6054 FTM cut off = 18162.0
"@ },
    [PSCustomObject]@{ ID="ETX-260904-0428"; RawID="ETX-260904-0428-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2237"; FTM="6548"; Group="GS+PBS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2734 TSB cut off = 8202.0 FTM -ve control = 6054 FTM cut off = 18162.0
"@ },
    [PSCustomObject]@{ ID="ETX-260904-0543"; RawID="ETX-260904-0543-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2919"; FTM="6496"; Group="GS+PBS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2734 TSB cut off = 8202.0 FTM -ve control = 6054 FTM cut off = 18162.0
"@ },
    [PSCustomObject]@{ ID="ETX-260904-0532"; RawID="ETX-260904-0532-4/5"; Record="091526-2222"; Method="d"; ATP="87468"; TSB="2188"; FTM="9106"; Group="GS+PBS"; Note=@"
Day 7 Sterility Read: Negative. Incubation ended on 15Sep26

091526-2222: TSB -ve control = 2734 TSB cut off = 8202.0 FTM -ve control = 6054 FTM cut off = 18162.0
"@ }
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
Write-Host "  Celsis Data Entry -- Batch 091526-2222 (34 samples)" -ForegroundColor Cyan
Write-Host "  ATP 87468 | GS: TSB 2566, FTM 5894 | GS+PBS: TSB 2734, FTM 6054" -ForegroundColor Cyan
Write-Host "  Mode: Enter-Only (Press ENTER to fill, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

for ($index = 0; $index -lt $Playlist.Count; $index++) {
    $Track = $Playlist[$index]

    Write-Host ""
    Write-Host ("[{0}/{1}] Next Sample: {2} (Group {3})" -f ($index + 1), $Playlist.Count, $Track.ID, $Track.Group) -ForegroundColor Yellow
    Write-Host "  Record=$($Track.Record) | Method=$($Track.Method) | ATP=$($Track.ATP) | TSB=$($Track.TSB) | FTM=$($Track.FTM)" -ForegroundColor Gray

    # Auto-copy correct note to clipboard
    try {
        Set-Clipboard -Value $Track.Note
        Write-Host "  [COPIED] Correct $($Track.Group) Test Note copied to clipboard!" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Clipboard copy failed" -ForegroundColor DarkGray
    }

    $prompt = ("Press [ENTER] to inject {0} (or 'q' to quit): " -f $Track.ID)
    $resp = Read-Host -Prompt $prompt
    if ($resp -match "^[Qq]") {
        Write-Host "Operation cancelled by user." -ForegroundColor Yellow
        break
    }

    Write-Host "  -> Injecting fields in 2 seconds... Switch to browser now!" -ForegroundColor Magenta
    Start-Sleep -Seconds 2

    # Standard 16-field keystroke sequence (stops before Save)
    Send-ValueAndTab $Track.Record
    Send-ValueAndTab $Track.Method
    Send-ValueAndTab "N/A"
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
    Send-ValueAndTab "y"
    Send-ValueAndTab "y"
    Send-ValueAndTab "y"
    Send-ValueAndTab "y"
    Send-ValueAndTab "p"

    Write-Host "  [DONE] $($Track.ID) injected! Please verify fields and paste Test Note, then save manually." -ForegroundColor Green
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  All items completed! Good job." -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
