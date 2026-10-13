import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import MultipleLocator, FixedLocator, StrMethodFormatter

# ======================
# 1. データの準備
# ======================
data = {
    'Group': ['Female'] * 4 + ['Male'] * 4 + ['Pregnant'] * 4,
    'Concentration': [
        165.5491, 0, 0, 0,
        0, 0, 0, 0,
        13200, 5652, 1220.466, 1860.652
    ]
}

df = pd.DataFrame(data)
group_order = ['Female', 'Male', 'Pregnant']

# ======================
# 2. 描画スタイル（論文用）
# ======================
sns.set_theme(style="white")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.weight": "bold",
    "axes.labelweight": "bold",
    "axes.linewidth": 2.0,
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "text.color": "black",
    "xtick.major.width": 2.0,
    "ytick.major.width": 2.0,
    "xtick.major.size": 6,
    "ytick.major.size": 6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "font.size": 18,
    "axes.labelsize": 20,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
})

# ======================
# 3. 図の作成
# ======================
fig, ax = plt.subplots(figsize=(8, 6))

sns.boxplot(
    x='Group',
    y='Concentration',
    data=df,
    order=group_order,
    showcaps=True,           # T字端
    showfliers=False,
    whis=1.5,
    boxprops=dict(facecolor='white', edgecolor='black', linewidth=2),
    medianprops=dict(color='black', linewidth=2),
    whiskerprops=dict(color='black', linewidth=2),
    capprops=dict(color='black', linewidth=2),
    ax=ax
)

sns.stripplot(
    x='Group',
    y='Concentration',
    data=df,
    order=group_order,
    color='black',
    size=7,
    jitter=0.15,
    linewidth=0,
    ax=ax
)

# ======================
# 4. Y軸設定（通常表記）
# ======================
y_max = df['Concentration'].max()
ax.set_ylim(0, y_max * 1.35)

# Y軸の設定（2000刻み、外向き）
ax.yaxis.set_major_locator(MultipleLocator(2000))
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.tick_params(axis='y', which='major', left=True, direction='out', length=6, width=2)

# X軸の設定：ラベル直下の線は消し、項目間（0.5, 1.5）に区切り線を入れる
ax.xaxis.set_minor_locator(FixedLocator([0.5, 1.5]))
ax.tick_params(axis='x', which='minor', bottom=True, direction='out', length=10, width=2, color='black')
ax.tick_params(axis='x', which='major', bottom=False) # ラベル位置の線は非表示

# Y軸ラベルは軸に沿って配置
ax.set_ylabel('Serum Relaxin', fontsize=24, fontweight='bold', labelpad=20)

# 単位 (pg/ml) のみを軸の上に配置
ax.text(
    -0.15,           # 位置の微調整（数値の左端付近）
    1.02,           # 軸のすぐ上
    '(pg/ml)',
    ha='left',
    va='bottom',
    fontsize=16,
    fontweight='bold',
    transform=ax.transAxes
)

# ======================
# 5. 有意差アノテーション
# ======================
p_values = {
    ('Male', 'Pregnant'): 0.006704,
    ('Female', 'Pregnant'): 0.024218,
}

def add_annotation(ax, g1, g2, p, y_start, y_height):
    if p < 0.001:
        stars = '***'
    elif p < 0.01:
        stars = '**'
    elif p < 0.05:
        stars = '*'
    else:
        return

    x = {name: i for i, name in enumerate(group_order)}
    x1, x2 = x[g1], x[g2]

    ax.plot(
        [x1, x1, x2, x2],
        [y_start, y_start + y_height, y_start + y_height, y_start],
        lw=2,
        c='black'
    )

    ax.text(
        (x1 + x2) / 2,
        y_start + y_height,
        stars,
        ha='center',
        va='bottom',
        fontsize=24,
        fontweight='bold'
    )

# Male vs Pregnant (x=1 to 2) -> 下段
add_annotation(ax, 'Male', 'Pregnant', p_values[('Male', 'Pregnant')],
               y_start=y_max * 1.05, y_height=y_max * 0.07)

# Female vs Pregnant (x=0 to 2) -> 上段
add_annotation(ax, 'Female', 'Pregnant', p_values[('Female', 'Pregnant')],
               y_start=y_max * 1.15, y_height=y_max * 0.07)

# ======================
# 6. 仕上げ・保存
# ======================
ax.set_xlabel("")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# 保存 (1200 DPI PNG および PDF)
plt.savefig('elisa_boxplot_bw_1200dpi.png', dpi=1200, bbox_inches='tight')
plt.savefig('elisa_boxplot_bw_1200dpi.pdf', bbox_inches='tight')
print("Saved to elisa_boxplot_bw_1200dpi.png and elisa_boxplot_bw_1200dpi.pdf")
plt.show()
