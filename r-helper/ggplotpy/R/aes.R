#' Build ggplot2 aes from string expressions (Python bridge)
#' @export
aes_from_strings <- function(...) {
  mapping <- list(...)
  if (length(mapping) == 0L) {
    return(ggplot2::aes())
  }
  exprs <- lapply(mapping, function(s) {
    if (!is.character(s) || length(s) != 1L) {
      stop("Each aes mapping must be a single character expression", call. = FALSE)
    }
    rlang::parse_expr(s)
  })
  names(exprs) <- names(mapping)
  do.call(ggplot2::aes, exprs)
}
