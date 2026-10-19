param([Parameter(Mandatory=$true)][string]$Profile,[Parameter(Mandatory=$true)][string]$Target)
$ErrorActionPreference='Stop'
$base=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$data=Get-Content -LiteralPath $Profile -Raw -Encoding utf8 | ConvertFrom-Json
$settings=$data.configuration
$core=[Reflection.Assembly]::LoadFrom((Join-Path $base '00_Reference\Tools\NYASM\app\Nyquest.Core.dll'))
$bin=[Reflection.Assembly]::LoadFrom((Join-Path $base '00_Reference\Tools\NYASM\app\Nyquest.Bin.dll'))
$body=[Nyquest.Core.MaskRomManager]::GetBody([string]$settings.Id)
foreach($property in $settings.PSObject.Properties){
    if($property.Name -in @('Id','Pins')){continue}
    $body.($property.Name)=$property.Value
}
$body.IsCProject=$true
foreach($spec in $settings.Pins){
    $pin=@($body.Pins | Where-Object {$_.Port.ToString() -eq $spec.Port -and $_.Feet -eq $spec.Bit})
    if($pin.Count -ne 1){throw 'Profile pin must identify one physical port bit'}
    $pin[0].Type=$spec.Type
}
$type=$core.GetType('Nyquest.Core.NY8ConfigBlockConverter')
$converter=[Activator]::CreateInstance($type,[object[]]@($body))
[byte[]]$bytes=$type.GetMethod('Convert',[type[]]@()).Invoke($converter,@())
$result=[Nyquest.Core.ConfigBlockConvertResult]::new()
$result.ConvertedData=$bytes
$list=[Activator]::CreateInstance([Collections.Generic.List[Nyquest.Core.IExternalRiffSerializable]])
$cfgType=$bin.GetType('Nyquest.Configure.Core.NY8ConfigureFile')
$cfg=[Activator]::CreateInstance($cfgType,[object[]]@($body.Id,$result,$list))
if(Test-Path -LiteralPath $Target){throw 'Choose a fresh configuration target'}
if(-not [Nyquest.Configure.ConfigureFileManager]::Write($Target,$cfg)){throw 'Configuration serialization requires success'}
Write-Output ('Configuration created: '+$Target)
