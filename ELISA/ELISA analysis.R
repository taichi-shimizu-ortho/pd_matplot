# 必要なライブラリをインストール（初回のみ）
install.packages("dunn.test")

# 1. データの入力
# 添付画像に基づき、データセットを作成します
concentration <- c(13200, 5652, 1220.466, 1860.652,  # pregnant (妊娠マウス)
                   165.5491, 0, 0, 0,               # female (非妊娠雌)
                   0, 0, 0, 0)                     # male (雄)

group <- factor(c(rep("pregnant", 4), rep("female", 4), rep("male", 4)))

data_relx <- data.frame(concentration, group)

# 2. Kruskal-Wallis H検定の実行
kruskal_result <- kruskal.test(concentration ~ group, data = data_relx)

print("Kruskal-Wallis H検定結果:")
print(kruskal_result)

# P値を取得し、後続のPythonコードで利用するために表示
p_value <- kruskal_result$p.value
cat("\nKruskal-Wallis P-value:", p_value, "\n")

# 必要なライブラリをインストール（まだインストールしていない場合）
install.packages("dunn.test") 
library(dunn.test)

# 1. データの再定義（前のステップから引き継いでいる場合は不要ですが、念のため記載）
concentration <- c(13200, 5652, 1220.466, 1860.652,  # pregnant
                   165.5491, 0, 0, 0,               # female
                   0, 0, 0, 0)                     # male

group <- factor(c(rep("pregnant", 4), rep("female", 4), rep("male", 4)))

# 2. Dunnの多重比較検定を実行
# method="bonferroni" でボンフェローニ補正を適用します
dunn_result <- dunn.test(concentration, group, 
                         method="bonferroni", 
                         wrap=TRUE, 
                         label=TRUE)

print("--- Dunnの多重比較検定結果（Bonferroni補正） ---")
print(dunn_result)

# P値の行列（比較結果）をより分かりやすく表示
cat("\n比較の組み合わせとBonferroni補正済みP値:\n")
# 比較対象の群のラベル
labels <- levels(group)
# P値の行列
p_matrix <- matrix(dunn_result$p.value, ncol = length(labels), byrow = TRUE)
colnames(p_matrix) <- labels
rownames(p_matrix) <- labels

# 下三角行列（重複を避けるため）を表示
p_matrix[upper.tri(p_matrix, diag = TRUE)] <- NA
print(p_matrix)