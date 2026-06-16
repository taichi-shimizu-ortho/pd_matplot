import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 1. データの準備
x_data = np.array([
    100, 50, 25, 12.5, 6.25, 3.125, 1.5625, 0, 
    50, 25, 12.5, 6.25, 3.125, 1.5625, 0.78125, 0.78125, 0
])
y_data = np.array([
    0.66, 0.913, 0.381, 0.181, 0.065, 0.069, 0.161, 0.134, 
    0.43, 0.25, 0.513, 0.345, 0.863, 0.113, 0.451, 0.574, 0.307
])

# 4PLモデルの関数定義
def fourPL(x, A, B, C, D):
    return D + (A - D) / (1.0 + (x / C) ** B)

# 初期値推定 [A, B, C, D]
initial_guess = [min(y_data), 1.0, np.median(x_data[x_data > 0]), max(y_data)]

# 2. ロバスト最適化による仮フィッティング
# 修正点: method='trf' を追加し、maxfev を max_nfev に変更しました
popt_robust, _ = curve_fit(
    fourPL, x_data, y_data, 
    p0=initial_guess, 
    method='trf',       # アルゴリズムをtrfに変更
    loss='soft_l1',     # 外れ値に強い損失関数
    f_scale=0.1, 
    max_nfev=10000      # trf用の最大試行回数
)

# 3. 残差（曲線と実際のデータの差）の計算と外れ値の特定
y_pred = fourPL(x_data, *popt_robust)
residuals = np.abs(y_data - y_pred)

# 閾値の設定（残差の標準偏差の1.5倍以上離れているものを外れ値とする）
threshold = np.std(residuals) * 1.5 

# 正常値(Inlier)と外れ値(Outlier)のマスクを作成
inlier_mask = residuals < threshold
outlier_mask = ~inlier_mask

# データを分割
x_inliers = x_data[inlier_mask]
y_inliers = y_data[inlier_mask]
x_outliers = x_data[outlier_mask]
y_outliers = y_data[outlier_mask]

print(f"全データ数: {len(x_data)}")
print(f"除外された外れ値の数: {len(x_outliers)}")
for x_out, y_out in zip(x_outliers, y_outliers):
    print(f"  -> 除外データ: 濃度={x_out}, 吸光度={y_out}")

# 4. 正常なデータ(Inliers)のみを使って最終フィッティング
# こちらはデフォルトのアルゴリズム(lm)で計算するため maxfev を使用
popt_final, _ = curve_fit(fourPL, x_inliers, y_inliers, p0=popt_robust, maxfev=10000)

# プロット用の滑らかなX軸データを作成
x_fit = np.logspace(np.log10(0.1), np.log10(max(x_data)), 500)
y_fit_final = fourPL(x_fit, *popt_final)

# 最終パラメータの出力
print(f"\n" + "="*50)
print(f"4PL Curve Parameters (popt_final):")
print(f"="*50)
print(f"A (min asymptote): {popt_final[0]}")
print(f"B (Hill slope): {popt_final[1]}")
print(f"C (EC50): {popt_final[2]}")
print(f"D (max asymptote): {popt_final[3]}")
print(f"="*50)
print(f"\nFor HTML, copy the following values to FOUR_PL:")
print(f"const FOUR_PL = {{")
print(f"  A: {popt_final[0]},")
print(f"  B: {popt_final[1]},")
print(f"  C: {popt_final[2]},")
print(f"  D: {popt_final[3]}")
print(f"}};")

# 5. グラフの描画
plt.figure(figsize=(9, 6))

# x=0を対数グラフに描画するための処理
x_inliers_plot = np.where(x_inliers == 0, 0.1, x_inliers)
x_outliers_plot = np.where(x_outliers == 0, 0.1, x_outliers)

# 正常値と外れ値を色分けしてプロット
plt.scatter(x_inliers_plot, y_inliers, color='blue', s=60, label='Valid Data (Inliers)', alpha=0.8)
plt.scatter(x_outliers_plot, y_outliers, color='gray', s=80, marker='x', label='Outliers (Excluded)', alpha=0.8)

# 最終的な検量線をプロット
plt.plot(x_fit, y_fit_final, color='red', linewidth=2, label='Final 4PL Fit Curve')

# グラフの装飾
plt.xscale('log')
plt.xlabel('Concentration')
plt.ylabel('Absorbance')
plt.title('ELISA Standard Curve with Outlier Removal')
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)

# x=0.1を「0」として表示
ticks = [0.1, 1, 10, 100]
labels = ['0', '1', '10', '100']
plt.xticks(ticks, labels)

plt.show()