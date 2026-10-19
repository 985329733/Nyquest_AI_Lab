param(
    [Parameter(Mandatory=$true)][string]$SdkPath,
    [Parameter(Mandatory=$true)][string]$AssemblerPath,
    [Parameter(Mandatory=$true)][string]$NyidePath,
    [Parameter(Mandatory=$true)][string]$ExamplesPath,
    [Parameter(Mandatory=$true)][string]$DatasheetDirectory
)
$ErrorActionPreference='Stop'
& python (Join-Path $PSScriptRoot '00_Reference\Scripts\setup_workspace.py') --sdk $SdkPath --assembler $AssemblerPath --nyide $NyidePath --examples $ExamplesPath --datasheets $DatasheetDirectory
exit $LASTEXITCODE
