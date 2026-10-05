$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Run setup.ps1 first.' }
& $python "$PSScriptRoot/app.py"
if ($LASTEXITCODE -ne 0) { throw 'Voice Studio stopped with an error.' }
