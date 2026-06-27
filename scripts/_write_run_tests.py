from pathlib import Path
root = Path(r"c:\ProfDM_Rproject\Ggplot2PY")
ps1 = """# OOM-safe tiered test runner for ggplotpy (Windows)
param(
    [ValidateSet('tier0', 'tier1', 'all', 'heavy')]
    [string]$Tier = 'tier0'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:GGPLOTPY_SKIP_NOTEBOOKS = '1'

function Invoke-Tier0 {
    $env:GGPLOTPY_SKIP_INTEGRATION = '1'
    Remove-Item Env:GGPLOTPY_RUN_HEAVY -ErrorAction SilentlyContinue
    python -m pytest tests/unit -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Invoke-Tier1 {
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    Remove-Item Env:GGPLOTPY_RUN_HEAVY -ErrorAction SilentlyContinue
    $files = Get-ChildItem -Path (Join-Path $Root 'tests/integration') -Filter 'test_*.py' | Sort-Object Name
    if (-not $files) {
        Write-Host 'No integration test files found.'
        return
    }
    $failed = @()
    foreach ($f in $files) {
        Write-Host \"=== T1: $($f.Name) ===\"
        python -m pytest $f.FullName -q
        if ($LASTEXITCODE -ne 0) { $failed += $f.Name }
    }
    if ($failed.Count -gt 0) {
        Write-Host \"Tier1 FAILED: $($failed -join ', ')\"
        exit 1
    }
    Write-Host 'Tier1: all integration files passed.'
}

function Invoke-Heavy {
    $env:GGPLOTPY_RUN_HEAVY = '1'
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    python -m pytest tests/ -q -m 'not slow'
    exit $LASTEXITCODE
}

switch ($Tier) {
    'tier0' { Invoke-Tier0 }
    'tier1' { Invoke-Tier1 }
    'all'   { Invoke-Tier0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; Invoke-Tier1 }
    'heavy' { Invoke-Heavy }
}
"""
sh = """#!/usr/bin/env bash
# OOM-safe tiered test runner for ggplotpy (Unix)
set -euo pipefail
ROOT=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\"
cd \"$ROOT\"
export GGPLOTPY_SKIP_NOTEBOOKS=1
TIER=\"${1:-tier0}\"

tier0() {
  export GGPLOTPY_SKIP_INTEGRATION=1
  unset GGPLOTPY_RUN_HEAVY || true
  python -m pytest tests/unit -q
}

tier1() {
  unset GGPLOTPY_SKIP_INTEGRATION || true
  unset GGPLOTPY_RUN_HEAVY || true
  mapfile -t files < <(find tests/integration -maxdepth 1 -name 'test_*.py' | sort)
  if ((${#files[@]} == 0)); then
    echo 'No integration test files found.'
    return 0
  fi
  failed=()
  for f in \"${files[@]}\"; do
    echo \"=== T1: $(basename \"$f\") ===\"
    if ! python -m pytest \"$f\" -q; then
      failed+=(\"$(basename \"$f\")\")
    fi
  done
  if ((${#failed[@]} > 0)); then
    echo \"Tier1 FAILED: ${failed[*]}\"
    exit 1
  fi
  echo 'Tier1: all integration files passed.'
}

heavy() {
  export GGPLOTPY_RUN_HEAVY=1
  unset GGPLOTPY_SKIP_INTEGRATION || true
  python -m pytest tests/ -q -m 'not slow'
}

case \"$TIER\" in
  tier0) tier0 ;;
  tier1) tier1 ;;
  all) tier0; tier1 ;;
  heavy) heavy ;;
  *) echo \"Unknown tier: $TIER (tier0|tier1|all|heavy)\" >&2; exit 2 ;;
esac
"""
(root / "scripts/run_tests.ps1").write_text(ps1, encoding="utf-8", newline="\r\n")
(root / "scripts/run_tests.sh").write_text(sh, encoding="utf-8", newline="\n")
print("ok")
