$taskName = "CelsisAutoSave10Runner"
$workDir = "c:\Users\qchen\OneDrive - Professional Compounding Centers of America, Inc\Documents\Celsis"
$batPath = Join-Path $workDir "run_auto_save_and_transition_10_samples.bat"

# Clean up any existing task
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create action to launch CMD interactively
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batPath`"" -WorkingDirectory $workDir

# Create trigger (run immediately / in 2 seconds)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(2)

# Set interactive principal so it pops up on the active user desktop
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register and start
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force
Start-ScheduledTask -TaskName $taskName

Write-Host "SUCCESS: Visible Task '$taskName' triggered in user desktop session!"
