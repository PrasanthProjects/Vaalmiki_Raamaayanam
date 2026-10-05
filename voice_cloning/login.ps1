$ErrorActionPreference = 'Stop'
$env:HF_HOME = Join-Path $PSScriptRoot 'models'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Run setup.ps1 first.' }
& $python -c "from huggingface_hub import login; login(add_to_git_credential=False)"
if ($LASTEXITCODE -ne 0) { throw 'Login failed.' }
