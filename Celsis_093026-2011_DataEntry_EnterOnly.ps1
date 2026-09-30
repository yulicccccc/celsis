# Celsis Data Entry Automation — Enter-Only Mode
# Batch: 093026-2011 | Samples: 37
# Safety: Enter-Only mode. Q to quit. This script NEVER clicks Save or Submit.
# Note: Automatically copies the appropriate control-group LIMS Note to clipboard for each sample.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartDate = "09/23/2026"
$EndDate   = "09/30/2026"
$GlobalATP = "85546"

$Playlist = @(
    [PSCustomObject]@{ ID="ETX-260921-0162"; RawID="ETX-260921-0162-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2134"; FTM="9486"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0193"; RawID="ETX-260921-0193-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2100"; FTM="7867"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0169"; RawID="ETX-260921-0169-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2544"; FTM="4936"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0197"; RawID="ETX-260921-0197-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2246"; FTM="6860"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0218"; RawID="ETX-260921-0218-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2310"; FTM="5191"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0154"; RawID="ETX-260921-0154-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2364"; FTM="6559"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0175"; RawID="ETX-260921-0175-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2955"; FTM="5125"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0152"; RawID="ETX-260921-0152-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2719"; FTM="6625"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0130"; RawID="ETX-260921-0130-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2627"; FTM="5847"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0110"; RawID="ETX-260921-0110-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2395"; FTM="5561"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0105"; RawID="ETX-260921-0105-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2756"; FTM="6027"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0145"; RawID="ETX-260921-0145-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="1993"; FTM="9471"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0103"; RawID="ETX-260921-0103-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="3077"; FTM="5176"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0133"; RawID="ETX-260921-0133-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2890"; FTM="4552"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0159"; RawID="ETX-260921-0159-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2563"; FTM="5789"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0204"; RawID="ETX-260921-0204-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2192"; FTM="5913"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0212"; RawID="ETX-260921-0212-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2440"; FTM="5432"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0227"; RawID="ETX-260921-0227-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2383"; FTM="7762"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0158"; RawID="ETX-260921-0158-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2795"; FTM="9584"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0163"; RawID="ETX-260921-0163-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2279"; FTM="6631"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0180"; RawID="ETX-260921-0180-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2459"; FTM="7416"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0172"; RawID="ETX-260921-0172-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2782"; FTM="6691"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0168"; RawID="ETX-260921-0168-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2746"; FTM="7013"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0190"; RawID="ETX-260921-0190-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2390"; FTM="5911"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0225"; RawID="ETX-260921-0225-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2701"; FTM="7673"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0222"; RawID="ETX-260921-0222-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2541"; FTM="7047"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0217"; RawID="ETX-260921-0217-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2543"; FTM="7102"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0229"; RawID="ETX-260921-0229-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2447"; FTM="7008"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0136"; RawID="ETX-260921-0136-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2429"; FTM="6515"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0165"; RawID="ETX-260921-0165-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2671"; FTM="6522"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0149"; RawID="ETX-260921-0149-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2761"; FTM="6646"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0224"; RawID="ETX-260921-0224-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2602"; FTM="8235"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0164"; RawID="ETX-260921-0164-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2216"; FTM="5318"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0196"; RawID="ETX-260921-0196-4/5"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2211"; FTM="5291"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0106"; RawID="ETX-260921-0106-4/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2500"; FTM="8462"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0121"; RawID="ETX-260921-0121-6/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2025"; FTM="7265"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" },
    [PSCustomObject]@{ ID="ETX-260921-0108"; RawID="ETX-260921-0108-6/6"; Record="093026-2011"; Method="m"; ATP="85546"; TSB="2807"; FTM="5266"; Group="GS"; Note="TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5" }
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
Write-Host "  Celsis Data Entry -- Batch 093026-2011 (37 samples)" -ForegroundColor Cyan
Write-Host "  ATP 85546 | GS: TSB 1907, FTM 7381" -ForegroundColor Cyan
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
