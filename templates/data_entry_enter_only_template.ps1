# Celsis Enter-only PowerShell template
# Synthetic example only.

$StartDate = "01/01/2099"
$EndDate   = "01/08/2099"
$ATP       = "100000"

$Playlist = @(
    [PSCustomObject]@{
        ID="ETX-990101-0001"
        Record="010899-0000"
        Method="m"
        ATP=$ATP
        TSB="1234"
        FTM="4567"
        Note="SYNTHETIC EXAMPLE"
    }
)

# Locked logical sequence:
# Record → Method → N/A → skip 2 → ml → Start → End → y
# → ATP → TSB → FTM → y → y → y → y → p
#
# Never click Save / Submit automatically.
