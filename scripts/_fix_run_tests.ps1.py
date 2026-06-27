from pathlib import Path
p = Path(r"c:\ProfDM_Rproject\Ggplot2PY\scripts\run_tests.ps1")
text = p.read_text(encoding="utf-8")
text = text.replace(
    """function Invoke-Tier1 {
    Write-Host "=== Tier1 (integration, one file per subprocess) ===" -ForegroundColor Cyan
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    $env:GGPLOTPY_RUN_HEAVY = "1"
""",
    """function Invoke-Tier1 {
    Write-Host "=== Tier1 (integration, one file per subprocess) ===" -ForegroundColor Cyan
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    Remove-Item Env:GGPLOTPY_RUN_HEAVY -ErrorAction SilentlyContinue
""",
)
if "ValidateSet(\"tier0\", \"tier1\", \"all\", \"heavy\")" not in text:
    text = text.replace(
        '[ValidateSet("tier0", "tier1", "all")]',
        '[ValidateSet("tier0", "tier1", "all", "heavy")]',
    )
if "function Invoke-Heavy" not in text:
    heavy = """

function Invoke-Heavy {
    Write-Host "=== Heavy (full tree, single process — may OOM) ===" -ForegroundColor Yellow
    $env:GGPLOTPY_RUN_HEAVY = "1"
    Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
    python -m pytest tests/ -q -m "not slow"
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    return 0
}
"""
    text = text.replace("\n$code = 0", heavy + "\n$code = 0")
    text = text.replace('    "all" {', '    "heavy" { $code = Invoke-Heavy }\n    "all" {')
p.write_text(text, encoding="utf-8", newline="\r\n")
print("run_tests.ps1 fixed")
