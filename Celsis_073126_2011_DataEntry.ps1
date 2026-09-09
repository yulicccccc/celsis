# Celsis Data Entry Automation — Enter-Only Mode
# Batch: 073126-2011 | Instrument: Advance 2
# Status: Prototype — Not validated for GxP use.

$StartDate = "07/24/2026"
$EndDate   = "07/31/2026"

$Playlist = @(
    [PSCustomObject]@{ ID="ETX-260723-0424"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="499"; FTM="1069" },
    [PSCustomObject]@{ ID="ETX-260723-0412"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="449"; FTM="855"  },
    [PSCustomObject]@{ ID="ETX-260723-0442"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="336"; FTM="800"  },
    [PSCustomObject]@{ ID="ETX-260723-0512"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="415"; FTM="903"  },
    [PSCustomObject]@{ ID="ETX-260723-0540"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="372"; FTM="930"  },
    [PSCustomObject]@{ ID="ETX-260723-0382"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="616"; FTM="970"  },
    [PSCustomObject]@{ ID="ETX-260723-0434"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="452"; FTM="770"  },
    [PSCustomObject]@{ ID="ETX-260723-0282"; Record="073126-2011"; Method="d"; ATP="112570"; TSB="409"; FTM="887"  }
)

$WshShell = New-Object -ComObject WScript.Shell

function Send-Field {
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
Write-Host " Celsis Data Entry - 073126-2011 (8 samples)" -ForegroundColor Cyan
Write-Host " ATP 112570 | TSB control 1033 | FTM control 2450" -ForegroundColor Cyan
Write-Host " Mode: Enter-Only (Press Enter to send, Q to quit)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

foreach ($Track in $Playlist) {
    Write-Host ""
    Write-Host ">>> Next sample: $($Track.ID)" -ForegroundColor Yellow
    Write-Host "    Record=$($Track.Record)  Method=$($Track.Method)  ATP=$($Track.ATP)  TSB=$($Track.TSB)  FTM=$($Track.FTM)" -ForegroundColor Gray

    $input = Read-Host "Place cursor in Test Record box and press [ENTER] (or Q to quit)"
    if ($input -eq "Q" -or $input -eq "q") {
        Write-Host "Stopped by user." -ForegroundColor Red
        break
    }

    Write-Host "Countdown: 3..." -ForegroundColor Red
    Start-Sleep -Seconds 1
    Write-Host "2..." -ForegroundColor Red
    Start-Sleep -Seconds 1
    Write-Host "1..." -ForegroundColor Red
    Start-Sleep -Seconds 1

    Send-Field $Track.Record
    Send-Field $Track.Method

    Send-Field "N/A" 200
    $WshShell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds 200
    $WshShell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds 200

    Send-Field "ml"
    Send-Field $StartDate
    Send-Field $EndDate
    Send-Field "y"
    Send-Field $Track.ATP
    Send-Field $Track.TSB
    Send-Field $Track.FTM

    for ($i = 1; $i -le 4; $i++) {
        Send-Field "y" 200
    }

    $WshShell.SendKeys("p")
    Start-Sleep -Milliseconds 300

    Write-Host "Done: $($Track.ID). Verify, paste Note, and Save manually." -ForegroundColor Green
}

Write-Host ""
Write-Host "Session finished. No auto-Save/Submit was performed." -ForegroundColor Cyan
