import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd

# 1. 検量線データの準備
x_data = np.array([
    100, 50, 25, 12.5, 6.25, 3.125, 1.5625, 0, 
    50, 25, 12.5, 6.25, 3.125, 1.5625, 0.78125, 0.78125, 0
])
y_data = np.array([
    0.66, 0.913, 0.381, 0.181, 0.065, 0.069, 0.161, 0.134, 
    0.43, 0.25, 0.513, 0.345, 0.863, 0.113, 0.451, 0.574, 0.307
])

# サンプルデータ
sample_ids = np.arange(1, 24)
sample_y = np.array([
    0.524, 0.667, 0.514, 0.355, 0.163, 0.453, 0.265, 0.338, 0.365, 0.376, 
    0.321, 0.491, 1.336, 0.99,  0.534, 0.079, 0.255, 0.214, 0.267, 0.31, 
    0.402, 0.448, 0.202
])

# 4PLモデルの関数
def fourPL(x, A, B, C, D):
    return D + (A - D) / (1.0 + (x / C) ** B)

# 4PLの逆関数（吸光度yから濃度xを計算）
def inverse_fourPL(y, A, B, C, D):
    min_val, max_val = min(A, D), max(A, D)
    # 検量線の範囲外の場合は計算不可(NaN)を返す
    if y <= min_val or y >= max_val:
        return np.nan
    
    val = (A - y) / (y - D)
    if val <= 0:
        return np.nan
    return C * (val ** (1 / B))

# 2. 検量線のフィッティング（前回と同じ処理）
initial_guess = [min(y_data), 1.0, np.median(x_data[x_data > 0]), max(y_data)]
popt_robust, _ = curve_fit(fourPL, x_data, y_data, p0=initial_guess, method='trf', loss='soft_l1', f_scale=0.1, max_nfev=10000)

y_pred = fourPL(x_data, *popt_robust)
residuals = np.abs(y_data - y_pred)
threshold = np.std(residuals) * 1.5 

inlier_mask = residuals < threshold
outlier_mask = ~inlier_mask

x_inliers = x_data[inlier_mask]
y_inliers = y_data[inlier_mask]
x_outliers = x_data[outlier_mask]
y_outliers = y_data[outlier_mask]

# 最終フィッティング
popt_final, _ = curve_fit(fourPL, x_inliers, y_inliers, p0=popt_robust, maxfev=10000)
A_fit, B_fit, C_fit, D_fit = popt_final

# 3. サンプルの濃度計算
sample_x = np.array([inverse_fourPL(y, *popt_final) for y in sample_y])

# 結果をコンソールに表示
print("=== サンプル濃度計算結果 ===")
results = pd.DataFrame({
    'Sample ID': sample_ids,
    'Absorbance (OD)': sample_y,
    'Calculated Conc.': sample_x
})
# NaNを「範囲外」として表示
results['Calculated Conc.'] = results['Calculated Conc.'].apply(lambda x: f"{x:.3f}" if pd.notnull(x) else "範囲外 (Out of Range)")
print(results.to_string(index=False))

# 4. グラフの描画
plt.figure(figsize=(10, 7))

# 検量線用の滑らかなX軸データ
x_fit = np.logspace(np.log10(0.1), np.log10(max(x_data)), 500)
y_fit_final = fourPL(x_fit, *popt_final)

# x=0のプロット用処理
x_inliers_plot = np.where(x_inliers == 0, 0.1, x_inliers)
x_outliers_plot = np.where(x_outliers == 0, 0.1, x_outliers)

# 検量線のデータポイント
plt.scatter(x_inliers_plot, y_inliers, color='blue', s=60, label='Standard (Inliers)', alpha=0.5)
plt.scatter(x_outliers_plot, y_outliers, color='gray', s=80, marker='x', label='Standard (Outliers)', alpha=0.5)
plt.plot(x_fit, y_fit_final, color='red', linewidth=2, label='4PL Fit Curve')

# サンプルデータのプロット（計算できたものだけ）
valid_samples_mask = ~np.isnan(sample_x)
valid_sample_x = sample_x[valid_samples_mask]
valid_sample_y = sample_y[valid_samples_mask]

plt.scatter(valid_sample_x, valid_sample_y, color='green', s=100, marker='*', label='Samples', zorder=5)

# グラフの装飾
plt.xscale('log')
plt.xlabel('Concentration')
plt.ylabel('Absorbance')
plt.title('ELISA Standard Curve with Samples')
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)

ticks = [0.1, 1, 10, 100]
labels = ['0', '1', '10', '100']
plt.xticks(ticks, labels)

# 検量線の上限・下限を点線で示す
plt.axhline(y=min(A_fit, D_fit), color='orange', linestyle=':', alpha=0.7, label='Curve Min/Max')
plt.axhline(y=max(A_fit, D_fit), color='orange', linestyle=':', alpha=0.7)
# CSVファイルとして保存（文字化け防止のため utf-8-sig を指定）
results.to_csv('elisa_results.csv', index=False, encoding='utf-8-sig')

plt.show()