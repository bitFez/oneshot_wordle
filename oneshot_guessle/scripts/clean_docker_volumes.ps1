Param(
    [switch]$Force,
    [string[]]$Exclude,
    [switch]$Yes
)

<#
Safely list and optionally remove unused (dangling) Docker volumes.

By default this script will only show candidate volumes and their sizes.
Use `-Force` to actually remove the listed volumes. Use `-Exclude` to add
extra substrings (case-insensitive) that should NOT be removed (eg: 'postgres').

Example:
  .\scripts\clean_docker_volumes.ps1        # dry-run, shows candidates
  .\scripts\clean_docker_volumes.ps1 -Force  # remove candidates after confirmation
  .\scripts\clean_docker_volumes.ps1 -Exclude pgdata,postgres -Force
#>

function Write-ErrorAndExit($msg){ Write-Host $msg -ForegroundColor Red; exit 1 }

if (-not (Get-Command docker -ErrorAction SilentlyContinue)){
    Write-ErrorAndExit "Docker CLI not found in PATH. Install Docker Desktop or add docker to PATH."
}

# default exclude substrings (common DB / persistent volumes)
$defaultExcludes = @('postgres','pgdata','postgresql','pg_','mongo','mysql','db','redis')
if ($Exclude){ $excludeList = $defaultExcludes + $Exclude } else { $excludeList = $defaultExcludes }

Write-Host 'Scanning for dangling Docker volumes...'
$dangling = (& docker volume ls --filter dangling=true --format '{{.Name}}') -split "`n" | Where-Object { $_ -ne '' }

if (-not $dangling -or $dangling.Count -eq 0){ Write-Host "No dangling volumes found."; exit 0 }

$candidates = @()
foreach ($vol in $dangling) {
    $skip = $false
    foreach ($pat in $excludeList) {
        if ($vol.ToLower().IndexOf($pat.ToLower()) -ge 0) { $skip = $true; break }
    }
    if (-not $skip) { $candidates += $vol }
}

if (-not $candidates -or $candidates.Count -eq 0) { Write-Host "No candidate volumes (dangling and not excluded)."; exit 0 }

Write-Host "Found $($candidates.Count) candidate volumes (dangling & not excluded):" -ForegroundColor Cyan

[int]$i = 0
$info = @()
foreach ($vol in $candidates) {
    $i += 1
    # attempt to measure size using an ephemeral alpine container
    $size = "<unknown>"
    try {
        $mount = "${vol}:/v"
        $out = & docker run --rm -v $mount alpine sh -c 'du -sh /v 2>/dev/null || echo 0' 2>$null
        if ($out) { $size = $out -replace '\\s+/v$','' }
    } catch { $size = '<err>' }
    $info += [pscustomobject]@{ Index = $i; Name = $vol; Size = $size }
}

$info | Format-Table Index, Name, Size -AutoSize

if (-not $Force) {
    Write-Host ''
    Write-Host 'Dry run only - no volumes were removed.' -ForegroundColor Yellow
    Write-Host 'To delete the above volumes, re-run with the -Force switch.' -ForegroundColor Yellow
    exit 0
}

if (-not $Yes) {
    $confirm = Read-Host "Remove these $($info.Count) volumes? Type 'yes' to confirm"
    if ($confirm -ne 'yes') { Write-Host 'Aborted.'; exit 0 }
}

Write-Host "Removing volumes..." -ForegroundColor Green
$failed = @()
foreach ($v in $info) {
    try {
        & docker volume rm $($v.Name) | Out-Null
        Write-Host "Removed $($v.Name)" -ForegroundColor Green
    } catch {
        Write-Host "Failed to remove $($v.Name): $_" -ForegroundColor Red
        $failed += $v.Name
    }
}

if ($failed.Count -gt 0) { Write-Host "Failed to remove: $($failed -join ', ')" -ForegroundColor Red }
else { Write-Host "Done." -ForegroundColor Green }
