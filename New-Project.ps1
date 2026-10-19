param([string]$Name,[string]$Chip,[switch]$ListChips)
$ErrorActionPreference='Stop'
$templates=Join-Path $PSScriptRoot '00_Reference\Templates'
if($ListChips){
    Get-ChildItem -LiteralPath $templates -Directory -Filter '*_Validated' | ForEach-Object {
        $q=Join-Path $_.FullName 'Qualification_Verification.json'
        if(Test-Path -LiteralPath $q){$meta=Get-Content -LiteralPath $q -Raw -Encoding utf8 | ConvertFrom-Json;if($meta.status -eq 'PASS'){Write-Output $meta.chip}}
    }
    exit 0
}
if(-not $Chip -and $Name -match '_(NY8[A-Z0-9]+)$'){$Chip=$Matches[1]}
if(-not $Chip){throw 'Specify the exact -Chip model; use -ListChips to list qualified templates'}
$Chip=$Chip.ToUpperInvariant()
if($Chip -notmatch '^NY8[A-Z0-9]+$'){throw 'Invalid exact chip identifier'}
if(-not $Name){throw 'Specify -Name Category_01_ProductName'}
if($Name -notmatch ('_'+[regex]::Escape($Chip)+'$')){$Name=$Name+'_'+$Chip}
if($Name -notmatch '^[A-Za-z][A-Za-z0-9]*_[0-9]{2,}_[A-Za-z][A-Za-z0-9]*_NY8[A-Z0-9]+$'){throw 'Use Category_01_ProductName, with optional matching chip suffix'}
$source=Join-Path $templates ($Chip+'_Validated')
$q=Join-Path $source 'Qualification_Verification.json'
if(-not(Test-Path -LiteralPath $q)){throw ('No qualified template. Run Add-Chip.ps1 '+$Chip+' first; no fallback chip allowed.')}
$meta=Get-Content -LiteralPath $q -Raw -Encoding utf8 | ConvertFrom-Json
if($meta.status -ne 'PASS' -or $meta.chip -ne $Chip){throw 'Template qualification missing or mismatched'}
$target=Join-Path $PSScriptRoot ('02_Projects\'+$Name)
if(Test-Path -LiteralPath $target){throw 'Project already exists; refusing overwrite'}
Copy-Item -LiteralPath $source -Destination $target -Recurse
$project=Get-ChildItem -LiteralPath $target -Filter '*.naprj' | Select-Object -First 1
$old=$project.BaseName
$enc=[Text.UTF8Encoding]::new($false)
foreach($file in @(Get-ChildItem -LiteralPath $target -File | Where-Object {$_.Extension -in @('.naprj','.NySln') -or $_.Name -eq 'Makefile'})){
    [IO.File]::WriteAllText($file.FullName,[IO.File]::ReadAllText($file.FullName).Replace($old,$Name),$enc)
}
foreach($ext in @('.naprj','.NySln','.cb')){
    $path=Join-Path $target ($old+$ext)
    if(Test-Path -LiteralPath $path){Rename-Item -LiteralPath $path -NewName ($Name+$ext)}
}
Rename-Item -LiteralPath (Join-Path $target 'Qualification_Verification.json') -NewName 'Template_Qualification.json'
# Never carry a copied build's PASS as evidence for the new project.
foreach($file in @(Get-ChildItem -LiteralPath $target -File | Where-Object {$_.Extension -in @('.bin','.elf','.map','.lst','.log') -or $_.Name -in @('Build_Verification.json','Behavior_Verification.json','Workflow_Verification.json')})){
    Remove-Item -LiteralPath $file.FullName
}
Copy-Item -LiteralPath (Join-Path $templates 'Product_Requirement_Template.md') -Destination (Join-Path $target 'Product_Requirements.md')
& python (Join-Path $PSScriptRoot '00_Reference\Scripts\project_paths.py') repair $target
if($LASTEXITCODE -ne 0){throw 'Path relocation failed'}
$readme=Join-Path $target 'README_For_Engineer.md'
$prefix="# 新工程：$Name`r`n`r`n当前为复制的参考/资格母版，尚未实现新产品需求。请先完成Product_Requirements.md，再更新程序、行为场景和中文工程师交接。`r`n`r`n"
[IO.File]::WriteAllText($readme,$prefix+[IO.File]::ReadAllText($readme).Replace($old,$Name),$enc)
Write-Output ('Created: '+$target)
& (Join-Path $PSScriptRoot 'Build.ps1') -Project ('02_Projects\'+$Name)
