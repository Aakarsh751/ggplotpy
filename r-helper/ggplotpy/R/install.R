#' Ensure ggplot2 (and ggplotpy helper deps) are available
#'
#' Loads ggplot2 into the search path. Called from Python bootstrap/check_setup.
#'
#' @return Invisibly TRUE when ggplot2 loads successfully.
#' @export
ensure_ggplotpy <- function() {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop(
      "ggplot2 is not installed. Run: install.packages('ggplot2')",
      call. = FALSE
    )
  }
  suppressPackageStartupMessages(library(ggplot2))
  invisible(TRUE)
}
