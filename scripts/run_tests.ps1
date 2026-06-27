# ggplotpy tiered test runner (OOM-safe T1: one integration file per subprocess)
param(
    [ValidateSet("tier0", "tier1", "tier2", "tier3", "all")]
    [string]$Tier = "all"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:GGPLOTPY_SKIP_NOTEBOOKS = "1"

function Get-Tier1TestFiles {
    $patterns = @(
        @{ Path = "tests/integration"; Recurse = $true }
        @{ Path = "tests/parity"; Recurse = $false }
        @{ Path = "tests/gallery"; Recurse = $false }
        @{ Path = "tests/extensions"; Recurse = $false }
    )
    $files = @()
    foreach ($p in $patterns) {
        $dir = Join-Path $Root $p.Path
        if (-not (Test-Path $dir)) { continue }
        $files += Get-ChildItem -Path $dir -Filter "test_*.py" -Recurse:$p.Recurse -File
    }
    return $files | Sort-Object FullName -Unique
}

function Invoke-Tier0 {
    Write-Host "=== Tier0 (unit, single process) ===" -ForegroundColor Cyan
    $env:GGPLOTPY_SKIP_INTEGRATION = "1"
    Remove-Item Env:GGPLOTPY_RUN_HEAVY -ErrorAction SilentlyContinue
    python -m pytest tests/unit -q | Out-Host
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    return 0
}

function Invoke-Tier1 {
    Write-Host "=== Tier1 (integration + parity + gallery, one file per subprocess) ===" -ForegroundColor Cyan
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    $env:GGPLOTPY_RUN_HEAVY = "1"

    $files = Get-Tier1TestFiles
    if (-not $files -or $files.Count -eq 0) {
        Write-Host "No Tier1 test files found." -ForegroundColor Yellow
        return 0
    }

    $failed = @()
    $passed = @()
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($Root.Length + 1)
        Write-Host "`n--- $rel ---" -ForegroundColor DarkGray
        python -m pytest $f.FullName -q --tb=short | Out-Host
        if ($LASTEXITCODE -eq 0) {
            $passed += $rel
            Write-Host "PASS $rel" -ForegroundColor Green
        } else {
            $failed += $rel
            Write-Host "FAIL $rel (exit $LASTEXITCODE)" -ForegroundColor Red
        }
    }

    Write-Host "`n=== Tier1 summary ===" -ForegroundColor Cyan
    foreach ($p in $passed) { Write-Host "PASS $p" -ForegroundColor Green }
    foreach ($p in $failed) { Write-Host "FAIL $p" -ForegroundColor Red }
    Write-Host "Passed $($passed.Count)/$($files.Count)" -ForegroundColor $(if ($failed.Count -eq 0) { "Green" } else { "Yellow" })

    if ($failed.Count -gt 0) { return 1 }
    return 0
}



function Invoke-Tier3 {
    Write-Host "=== Tier3 (notebooks via nbclient, single process) ===" -ForegroundColor Cyan
    Remove-Item Env:GGPLOTPY_SKIP_NOTEBOOKS -ErrorAction SilentlyContinue
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    $env:GGPLOTPY_RUN_HEAVY = "1"

    $nbDir = Join-Path $Root "tests/notebooks"
    if (-not (Test-Path $nbDir)) {
        Write-Host "No tests/notebooks directory." -ForegroundColor Yellow
        return 0
    }
    python -m pytest $nbDir -q --tb=short | Out-Host
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    return 0
}
function Get-Tier2TestFiles {
    $dir = Join-Path $Root "tests/edge"
    if (-not (Test-Path $dir)) { return @() }
    return Get-ChildItem -Path $dir -Filter "test_*.py" -File | Sort-Object FullName
}

function Invoke-Tier2 {
    Write-Host "=== Tier2 (edge matrix, one file per subprocess) ===" -ForegroundColor Cyan
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    $env:GGPLOTPY_RUN_HEAVY = "1"

    $files = Get-Tier2TestFiles
    if (-not $files -or $files.Count -eq 0) {
        Write-Host "No Tier2 test files found." -ForegroundColor Yellow
        return 0
    }

    $failed = @()
    $passed = @()
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($Root.Length + 1)
        Write-Host "`n--- $rel ---" -ForegroundColor DarkGray
        python -m pytest $f.FullName -q --tb=short | Out-Host
        if ($LASTEXITCODE -eq 0) {
            $passed += $rel
            Write-Host "PASS $rel" -ForegroundColor Green
        } else {
            $failed += $rel
            Write-Host "FAIL $rel (exit $LASTEXITCODE)" -ForegroundColor Red
        }
    }

    Write-Host "`n=== Tier2 summary ===" -ForegroundColor Cyan
    foreach ($p in $passed) { Write-Host "PASS $p" -ForegroundColor Green }
    foreach ($p in $failed) { Write-Host "FAIL $p" -ForegroundColor Red }
    Write-Host "Passed $($passed.Count)/$($files.Count)" -ForegroundColor $(if ($failed.Count -eq 0) { "Green" } else { "Yellow" })

    if ($failed.Count -gt 0) { return 1 }
    return 0
}

$code = 0
switch ($Tier) {
    "tier0" { $code = Invoke-Tier0 }
    "tier1" { $code = Invoke-Tier1 }
    "tier2" { $code = Invoke-Tier2 }
    "tier3" { $code = Invoke-Tier3 }
    "all" {
        $c0 = Invoke-Tier0
        if ($c0 -ne 0) { $code = $c0 }
        else {
            $c1 = Invoke-Tier1
            if ($c1 -ne 0) { $code = $c1 } else {
            $c2 = Invoke-Tier2
            if ($c2 -ne 0) { $code = $c2 } else { $code = Invoke-Tier3 }
        }
        }
    }
}
exit $code
