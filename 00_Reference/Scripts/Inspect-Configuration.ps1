param([Parameter(Mandatory=$true)][string]$ProjectDir,[string]$Chip,[string]$ConfigBlock)
$ErrorActionPreference='Stop'
$base=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$projectPath=(Resolve-Path -LiteralPath $ProjectDir).Path
if(-not $Chip){
    $projects=@(Get-ChildItem -LiteralPath $projectPath -Filter '*.naprj')
    if($projects.Count -ne 1){throw 'Select one vendor project'}
    [xml]$xml=Get-Content -LiteralPath $projects[0].FullName -Raw
    $Chip=[string]$xml.Project.PropertyGroup[0].ChipId
}
if(-not $ConfigBlock){
    $make=[IO.File]::ReadAllText((Join-Path $projectPath 'Makefile'))
    $match=[regex]::Match($make,'(?m)^CB_FILE\s*:?=\s*([^\r\n]+)')
    if(-not $match.Success){throw 'Makefile requires CB_FILE'}
    $ConfigBlock=Join-Path $projectPath $match.Groups[1].Value.Trim()
}
$cb=(Resolve-Path -LiteralPath $ConfigBlock).Path
if((Split-Path $cb -Parent) -ne $projectPath){throw 'Configuration must belong to the project'}
$core=[Reflection.Assembly]::LoadFrom((Join-Path $base '00_Reference\Tools\NYASM\app\Nyquest.Core.dll'))
[void][Reflection.Assembly]::LoadFrom((Join-Path $base '00_Reference\Tools\NYASM\app\Nyquest.Bin.dll'))
$read=[Nyquest.Configure.ConfigureFileManager]::Read($cb)
if(-not $read.IsReadOk){throw 'Supply a readable vendor configuration'}
if($read.ConfigureFile.ChipName.ToString() -ne $Chip){throw 'Configuration container chip must match the selected project'}
$body=[Nyquest.Core.MaskRomManager]::GetBody($Chip)
$type=$core.GetType('Nyquest.Core.NY8ConfigBlockConverter')
$converter=[Activator]::CreateInstance($type,[object[]]@($body))
$decoded=$type.GetMethod('ConvertBack',[type[]]@([byte[]],[int],[Nyquest.Core.IConfigData])).Invoke($converter,[object[]]@($read.ConfigureFile.Data,0,$read.ConfigureFile.GenerateConfigBlockConvertConfigure))
if($decoded.Id.ToString() -ne $Chip){throw 'Decoded chip identity must match the selected project'}
$hasher=[Security.Cryptography.SHA256]::Create()
try{$cbHash=[BitConverter]::ToString($hasher.ComputeHash([IO.File]::ReadAllBytes($cb))).Replace('-','').ToLowerInvariant()}finally{$hasher.Dispose()}
$record=[ordered]@{schema_version=1;cb_sha256=$cbHash}
foreach($key in @('Id','HighOsc','LowOsc','IrcFreq','InstructionClock','Wdt','WdtEvent','WdtTimeBase','LvrSetting','LvrVoltage','PowerOnClock','ReadIoSource')){
    $record[$key]=$decoded.$key.ToString()
}
$record['Pins']=@($decoded.Pins | ForEach-Object {[ordered]@{Port=$_.Port.ToString();Bit=$_.Feet;Type=$_.Type.ToString()}})
$text=$record | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText((Join-Path $projectPath 'Configuration_Readback.json'),$text,[Text.UTF8Encoding]::new($false))
Write-Output ('Configuration decoded: '+$Chip)
