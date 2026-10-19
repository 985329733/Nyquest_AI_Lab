param([string]$Project, [switch]$SelectProject, [switch]$Isolated)
$ErrorActionPreference='Stop'
$arguments=@((Join-Path $PSScriptRoot '00_Reference\Scripts\build_project.py'))
if($Project){$arguments+=@('--project',$Project)}
if($Isolated){$arguments+='--isolated'}
& python @arguments
exit $LASTEXITCODE
