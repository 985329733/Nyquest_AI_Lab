param([Parameter(Mandatory=$true,Position=0)][string]$Chip,[string]$Evidence,[switch]$Inspect)
$ErrorActionPreference='Stop'
$argsList=@((Join-Path $PSScriptRoot '00_Reference\Scripts\add_chip.py'),$Chip)
if($Evidence){$argsList+=@('--evidence',$Evidence)}
if($Inspect){$argsList+='--inspect'}
& python @argsList
if($LASTEXITCODE -ne 0){throw 'Chip onboarding stopped. Read the missing evidence or validation error above; no chip may be guessed.'}
