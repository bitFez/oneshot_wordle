Param()

Write-Host "Compiling requirements/top_level_deps.in -> requirements/base.txt"

if (-not (Get-Command pip-compile -ErrorAction SilentlyContinue)) {
    Write-Error "pip-compile not found. Install with: pip install pip-tools"
    exit 1
}

pip-compile requirements/top_level_deps.in --output-file=requirements/base.txt
Write-Host "Wrote requirements/base.txt"
