Import-Module AudioDeviceCmdlets

# Get all commands in the AudioDeviceCmdlets module
$commands = Get-Command -Module AudioDeviceCmdlets

# Display information for each command
foreach ($command in $commands) {
    Write-Host "`nCommand: $($command.Name)" -ForegroundColor Cyan
    Write-Host "Parameters:" -ForegroundColor Yellow
    $parameters = $command.Parameters.Keys | Where-Object { $_ -notin [System.Management.Automation.PSCmdlet]::CommonParameters }
    foreach ($param in $parameters) {
        Write-Host "  - $param"
    }
}

# Display detailed information for Set-AudioDevice
Write-Host "`nDetailed information for Set-AudioDevice:" -ForegroundColor Magenta
Get-Help Set-AudioDevice -Detailed

# Get the default recording device
$recordingDevice = Get-AudioDevice -List | Where-Object { $_.Type -eq 'Recording' -and $_.Default -eq $true }

if ($null -eq $recordingDevice) {
    Write-Host "Could not find default recording device. Exiting script."
    exit
}
# this does not work yes
Set-AudioDevice -ID $recordingDevice.ID -PlaybackCommunicationMuteToggle
