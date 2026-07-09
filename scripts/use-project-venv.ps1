# Use this repo's Poetry venv (congressional-data-public/.venv).
# Run from repo root:  .\scripts\use-project-venv.ps1
#
# If another project's venv is active, Poetry's ``poetry run`` targets that
# interpreter and optional groups (codegen/click) will be missing.

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (Get-Command deactivate -ErrorAction SilentlyContinue) {
    deactivate
}
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
Remove-Item Env:VIRTUAL_ENV_PROMPT -ErrorAction SilentlyContinue

$activate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "No .venv yet. Run: poetry install --with dev,codegen" -ForegroundColor Yellow
    Set-Location $RepoRoot
    poetry install --with dev,codegen
    if (-not (Test-Path $activate)) {
        throw "Failed to create .venv under $RepoRoot"
    }
}

& $activate
Set-Location $RepoRoot
Write-Host "Using $RepoRoot\.venv (run: poetry run python -m codegen generate-all)" -ForegroundColor Green
