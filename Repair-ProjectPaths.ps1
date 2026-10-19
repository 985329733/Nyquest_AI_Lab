param([Parameter(Mandatory=$true)][string]$Project)
$ErrorActionPreference='Stop'
$p=if([IO.Path]::IsPathRooted($Project)){$Project}else{Join-Path $PSScriptRoot $Project}
& python (Join-Path $PSScriptRoot '00_Reference\Scripts\project_paths.py') repair $p
if($LASTEXITCODE -ne 0){throw 'Path repair failed'}
