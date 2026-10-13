# 必要なパッケージ
install.packages("dunn.test")
library(dunn.test)

# データ入力
concentration <- c(13200, 5652, 1220.466, 1860.652,
                   165.5491, 0, 0, 0,
                   0, 0, 0, 0)

group <- factor(c(rep("pregnant", 4),
                  rep("female", 4),
                  rep("male", 4)))

data_relx <- data.frame(concentration, group)

# 記述統計
aggregate(concentration ~ group, data_relx, function(x) {
  c(n = length(x),
    median = median(x),
    min = min(x),
    max = max(x))
})

# Shapiro-Wilk正規性検定
normality_results <- by(data_relx$concentration, data_relx$group, function(x) {
  if (length(unique(x)) == 1) {
    return("Shapiro-Wilk test not applicable: all values are identical.")
  } else {
    return(shapiro.test(x))
  }
})

print("Shapiro-Wilk normality test:")
print(normality_results)

# Kruskal-Wallis検定
kruskal_result <- kruskal.test(concentration ~ group, data = data_relx)

print("Kruskal-Wallis test:")
print(kruskal_result)

# Dunnの多重比較検定 Bonferroni補正
dunn_result <- dunn.test(data_relx$concentration,
                         data_relx$group,
                         method = "bonferroni",
                         wrap = TRUE,
                         label = TRUE)

print("Dunn's multiple comparison test with Bonferroni correction:")
print(dunn_result)

# 95%CIのみ
# データ入力
concentration <- c(13200, 5652, 1220.466, 1860.652,
                   165.5491, 0, 0, 0,
                   0, 0, 0, 0)

group <- factor(c(rep("pregnant", 4),
                  rep("female", 4),
                  rep("male", 4)))

data_relx <- data.frame(concentration, group)

# pregnant mice のみ抽出
pregnant_data <- subset(data_relx, group == "pregnant")

# 平均値の95%信頼区間
t_result <- t.test(pregnant_data$concentration, conf.level = 0.95)

# 結果表示
t_result

# 必要な値だけ取り出す
mean_pregnant <- mean(pregnant_data$concentration)
ci_mean <- t_result$conf.int

mean_pregnant
ci_mean
# 効果量----

wilcox.test(concentration ~ group,
            data = subset(data_relx, group %in% c("pregnant", "female")),
            conf.int = TRUE,
            conf.level = 0.95,
            exact = FALSE)
wilcox.test(concentration ~ group,
            data = subset(data_relx, group %in% c("pregnant", "male")),
            conf.int = TRUE,
            conf.level = 0.95,
            exact = FALSE)

