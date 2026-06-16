import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

DAYS = [0, 7, 14, 21, 28]


def parse_raw_csv(filepath: str) -> pd.DataFrame:
    """生CSVを読み込み、tidy形式のDataFrameに変換する。"""
    raw = pd.read_csv(filepath, header=0, encoding="utf-8-sig")

    # 空行で区切られた3ブロックを分割
    blocks = []
    current = []
    for _, row in raw.iterrows():
        if row.iloc[0] == "" or pd.isna(row.iloc[0]):
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(row)
    if current:
        blocks.append(current)

    records = []
    for rep_idx, block in enumerate(blocks, start=1):
        for row in block:
            num = int(row.iloc[0])
            pct_area = float(row.iloc[3])
            condition = "ITS-" if num <= 5 else "ITS+"
            day = DAYS[num - 1] if num <= 5 else DAYS[num - 6]
            records.append({
                "condition": condition,
                "day": day,
                "rep": rep_idx,
                "pct_area": pct_area,
            })

    return pd.DataFrame(records)


def save_tidy_csv(df: pd.DataFrame, filepath: str) -> None:
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"tidy CSV saved: {filepath}")


def plot_nodule_area(df: pd.DataFrame, output_path: str) -> None:
    """条件ごとに平均±SDの折れ線グラフを描画する。"""
    summary = (
        df.groupby(["condition", "day"])["pct_area"]
        .agg(mean="mean", sd="std")
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(7, 5))

    styles = {
        "ITS-": {"color": "steelblue", "marker": "o", "linestyle": "-"},
        "ITS+": {"color": "tomato",    "marker": "s", "linestyle": "-"},
    }

    for cond, grp in summary.groupby("condition"):
        s = styles[cond]
        ax.errorbar(
            grp["day"],
            grp["mean"],
            yerr=grp["sd"],
            label=cond,
            color=s["color"],
            marker=s["marker"],
            linestyle=s["linestyle"],
            capsize=4,
            linewidth=1.5,
            markersize=6,
        )

    ax.set_xlabel("Day", fontsize=12)
    ax.set_ylabel("Nodule area (%)", fontsize=12)
    ax.set_title("ATDC5 Nodule Area", fontsize=13)
    ax.set_xticks(DAYS)
    ax.legend(title="Condition", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"graph saved: {output_path}")
    plt.show()


def main():
    raw_path   = "atdc5_nodule.csv"
    tidy_path  = "atdc5_nodule_tidy.csv"
    graph_path = "atdc5_nodule_area.png"

    df = parse_raw_csv(raw_path)
    save_tidy_csv(df, tidy_path)
    plot_nodule_area(df, graph_path)


if __name__ == "__main__":
    main()
