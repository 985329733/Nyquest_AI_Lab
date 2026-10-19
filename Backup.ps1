param([Parameter(Mandatory=$true)][string]$Destination, [ValidateRange(1,100)][int]$Keep = 10)
$ErrorActionPreference = 'Stop'
& python (Join-Path $PSScriptRoot '00_Reference\Scripts\backup_base.py') --source $PSScriptRoot --destination $Destination --keep $Keep
if($LASTEXITCODE -ne 0){throw 'Read the backup diagnostic and verify the destination archive state.'}
