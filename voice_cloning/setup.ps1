$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$bootstrap = Join-Path $root '../production/tools/python/python.exe'
$uvDir = Join-Path $root '.bootstrap'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $root '.python'
$env:UV_PYTHON_BIN_DIR = Join-Path $root '.python-bin'
# Short build paths avoid MAX_PATH errors in older Python package builders.
$env:UV_CACHE_DIR = Join-Path $env:TEMP 'telugu-voice-uv'
if (!(Test-Path "$uvDir/bin/uv.exe")) {
    & $bootstrap -m pip install --target $uvDir uv
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the Python environment manager.' }
}
$uv = Join-Path $uvDir 'bin/uv.exe'
& $uv python install 3.10
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 download failed.' }
if (!(Test-Path "$root/.venv/Scripts/python.exe")) {
    & $uv venv --python 3.10 "$root/.venv"
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed.' }
}
& $uv pip install --python "$root/.venv/Scripts/python.exe" -r "$root/requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. See the error above.' }
Write-Host 'Setup complete. Run login.ps1 once, then run.ps1.'
