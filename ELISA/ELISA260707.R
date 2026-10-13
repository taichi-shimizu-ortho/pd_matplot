install.packages("dplyr")
install.packages("boot")
install.packages("dunn.test")

library(dplyr)
library(boot)
library(dunn.test)

# データ
concentration <- c(13200, 5652, 1220.466, 1860.652,
                   165.5491, 0, 0, 0,
                   0, 0, 0, 0)

group <- factor(c(rep("pregnant", 4),
                  rep("female", 4),
                  rep("male", 4)),
                levels = c("female", "male", "pregnant"))

data_relx <- data.frame(concentration, group)

# Kruskal-Wallis test
kruskal_result <- kruskal.test(concentration ~ group, data = data_relx)

# Dunn test
dunn_result <- dunn.test(concentration, group,
                         method = "bonferroni",
                         wrap = TRUE,
                         label = TRUE)

# bootstrap median CI function
median_fun <- function(data, indices) {
  median(data[indices])
}

boot_median_ci <- function(x, R = 10000) {
  set.seed(123)
  
  if (length(unique(x)) == 1) {
    return(c(lower = unique(x), upper = unique(x)))
  }
  
  boot_result <- boot(data = x, statistic = median_fun, R = R)
  ci <- boot.ci(boot_result, type = "perc")
  
  c(
    lower = ci$percent[4],
    upper = ci$percent[5]
  )
}

# summary table
summary_table <- data_relx %>%
  group_by(group) %>%
  summarise(
    n = n(),
    median = median(concentration),
    min = min(concentration),
    max = max(concentration),
    ci_lower = boot_median_ci(concentration)[1],
    ci_upper = boot_median_ci(concentration)[2],
    range = paste0(round(min, 2), "–", round(max, 2)),
    ci_95 = paste0(round(ci_lower, 2), "–", round(ci_upper, 2)),
    .groups = "drop"
  )

# p valueを手動で付与
summary_table <- summary_table %>%
  mutate(
    p_value = case_when(
      group == "female" ~ "0.024 vs pregnant",
      group == "male" ~ "0.007 vs pregnant",
      group == "pregnant" ~ "Reference"
    )
  )

print(summary_table)

cat("\nKruskal-Wallis p-value:", kruskal_result$p.value, "\n")
print(summary_table, width = Inf)

