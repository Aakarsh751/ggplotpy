# NSE Bridge — `aes_from_strings`

Design for ggplot2 non-standard evaluation from Python. Research §2.4; **D-P003**.

---

## Problem

ggplot2 `aes(x = wt, y = mpg)` captures **unquoted symbols** as quosures. Python cannot pass bare `wt`. Legacy `aes_string()` is deprecated.

---

## Solution

Layered approach:

1. **Primary:** Python passes **strings**; R helper parses each as an expression with `rlang::parse_expr` and splices into `ggplot2::aes()`.
2. **Pronoun:** `.data[["col"]]` for odd column names.
3. **Escape:** `R("interaction(a, b)")` for unmodeled expressions.

---

## Python surface

```python
aes(x="wt", y="mpg", color="factor(cyl)")
aes(x="log(wt)", color=".data[['wt']]")  # expression strings
```

Maps kwargs → named list → R helper (British `colour` accepted; normalize in helper if needed).

---

## R helper (`r-helper/ggplotpy/R/aes.R`)

```r
#' Build aes from string expressions (Python bridge)
#' @param mapping named list of character expressions
#' @export
aes_from_strings <- function(mapping) {
  exprs <- lapply(mapping, function(s) rlang::parse_expr(s))
  do.call(ggplot2::aes, exprs)
}
```

Export as `ggplotpy:::aes_from_strings` (companion package loaded with ggplotpy session).

**Emit path:**

```python
# Python (conceptual)
# aes(x="wt", y="mpg")
# → R: ggplotpy::aes_from_strings(list(x="wt", y="mpg"))
```

---

## Faceting formulas

Python passes formula **strings**; R converts via `stats::as.formula`:

```python
facet_wrap("~ cyl")
facet_grid("gear ~ cyl")
```

---

## Testing (T0 + T2)

Golden files under `tests/golden/aes/`:

| Case | Python | Assert |
|------|--------|--------|
| Bare column | `x="wt"` | Parsed symbol |
| Expression | `x="log(wt)"` | Call preserved |
| Factor | `color="factor(cyl)"` | Call preserved |
| Pronoun | `x='.data[["x"]]'` | Robust name |
| Multi-aes | several kwargs | All spliced |

Full plot `to_r()` goldens in T2 for integrated NSE.

---

## Failure modes

| Issue | Mitigation |
|-------|------------|
| Invalid R syntax in string | Python/R error with snippet + `last_r_code()` |
| Column name vs R reserved word | Document `.data[[]]` |
| ggplot2 4.0 S7 internals | Stay on public `aes()` only |

See also: `docs/user_interface.md`, `docs/architecture.md`.
