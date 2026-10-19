param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference='Stop'
& python (Join-Path $PSScriptRoot '00_Reference\Scripts\export_source.py') --destination $Destination
exit $LASTEXITCODE
