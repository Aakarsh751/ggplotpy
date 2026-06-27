#!/usr/bin/env bash
# ggplotpy tiered test runner (OOM-safe T1: one integration file per subprocess)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export GGPLOTPY_SKIP_NOTEBOOKS=1
TIER="${1:-all}"

run_tier0() {
  echo "=== Tier0 (unit, single process) ==="
  export GGPLOTPY_SKIP_INTEGRATION=1
  unset GGPLOTPY_RUN_HEAVY 2>/dev/null || true
  python -m pytest tests/unit -q
}

collect_tier1_files() {
  local -a out=()
  local d f
  if [[ -d tests/integration ]]; then
    while IFS= read -r -d '' f; do out+=("$f"); done < <(find tests/integration -name 'test_*.py' -print0 | sort -z)
  fi
  for d in tests/parity tests/gallery tests/extensions; do
    if [[ -d "$d" ]]; then
      for f in "$d"/test_*.py; do
        [[ -f "$f" ]] || continue
        out+=("$f")
      done
    fi
  done
  if ((${#out[@]} == 0)); then
    return 0
  fi
  printf '%s\0' "${out[@]}" | sort -z | tr '\0' '\n'
}

run_tier1() {
  echo "=== Tier1 (integration + parity + gallery, one file per subprocess) ==="
  unset GGPLOTPY_SKIP_INTEGRATION
  export GGPLOTPY_RUN_HEAVY=1

  mapfile -t files < <(collect_tier1_files)
  if ((${#files[@]} == 0)); then
    echo "No Tier1 test files found."
    return 0
  fi

  failed=()
  passed=()
  for f in "${files[@]}"; do
    echo ""
    echo "--- $f ---"
    if python -m pytest "$f" -q --tb=short; then
      passed+=("$f")
      echo "PASS $f"
    else
      failed+=("$f")
      echo "FAIL $f"
    fi
  done

  echo ""
  echo "=== Tier1 summary ==="
  for p in "${passed[@]}"; do echo "PASS $p"; done
  for p in "${failed[@]}"; do echo "FAIL $p"; done
  echo "Passed ${#passed[@]}/${#files[@]}"

  ((${#failed[@]} == 0))
}

run_tier2() {
  echo "=== Tier2 (edge matrix, one file per subprocess) ==="
  unset GGPLOTPY_SKIP_INTEGRATION
  export GGPLOTPY_RUN_HEAVY=1

  [[ -d tests/edge ]] || { echo "No tests/edge directory."; return 0; }
  failed=()
  passed=()
  for f in tests/edge/test_*.py; do
    [[ -f "$f" ]] || continue
    echo ""
    echo "--- $f ---"
    if python -m pytest "$f" -q --tb=short; then
      passed+=("$f"); echo "PASS $f"
    else
      failed+=("$f"); echo "FAIL $f"
    fi
  done
  echo ""
  echo "=== Tier2 summary ==="
  for p in "${passed[@]}"; do echo "PASS $p"; done
  for p in "${failed[@]}"; do echo "FAIL $p"; done
  echo "Passed ${#passed[@]}/$((${#passed[@]} + ${#failed[@]}))"
  ((${#failed[@]} == 0))
}

run_tier3() {
  echo "=== Tier3 (notebooks via nbclient, single process) ==="
  unset GGPLOTPY_SKIP_NOTEBOOKS
  unset GGPLOTPY_SKIP_INTEGRATION
  export GGPLOTPY_RUN_HEAVY=1
  [[ -d tests/notebooks ]] || { echo "No tests/notebooks directory."; return 0; }
  python -m pytest tests/notebooks -q --tb=short
}

run_heavy() {
  echo "=== Heavy (full tree, single process - may OOM) ==="
  export GGPLOTPY_RUN_HEAVY=1
  unset GGPLOTPY_SKIP_INTEGRATION 2>/dev/null || true
  python -m pytest tests/ -q -m "not slow"
}

code=0
case "$TIER" in
  tier0) run_tier0 || code=$? ;;
  tier1) run_tier1 || code=$? ;;
  tier2) run_tier2 || code=$? ;;
  tier3) run_tier3 || code=$? ;;
  heavy) run_heavy || code=$? ;;
  all)
    run_tier0 || code=$?
    if (( code == 0 )); then run_tier1 || code=$?; fi
    if (( code == 0 )); then run_tier2 || code=$?; fi
    if (( code == 0 )); then run_tier3 || code=$?; fi
    ;;
  *)
    echo "Usage: $0 [tier0|tier1|tier2|tier3|all|heavy]" >&2
    exit 2
    ;;
esac
exit "$code"



