library(ggplot2)
p <- ggplot(data)
p <- p + aes(x = wt, y = mpg)
p <- p + geom_point()
