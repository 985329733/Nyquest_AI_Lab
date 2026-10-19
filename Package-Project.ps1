param([Parameter(Mandatory=$true)][string]$Project)
$ErrorActionPreference='Stop'
$path=if([IO.Path]::IsPathRooted($Project)){$Project}else{Join-Path $PSScriptRoot $Project}
& python (Join-Path $PSScriptRoot '00_Reference\Scripts\package_demo.py') $path
exit $LASTEXITCODE
