"""東日本レインズ「Market Watch」2026年9月度の中古マンション成約状況から、記事用の2枚組グラフを描く。

図1: 東京都区部の成約㎡単価と、都心3区が都区部の成約件数に占める割合（月次）
図2: 横浜市・川崎市の成約㎡単価と平均築年数（月次）

数値は同機構が公開している月例速報（サマリーレポート・データ）の集計値を転記したもの。
都心3区の割合は「都心3区の成約件数 ÷ 都心3区・城東・城南・城西・城北の合計（＝都区部）」で当社が算出。

出力: public/images/blog/tokyo23ku-mansion-202609(-en).png / yokohama-kawasaki-mansion-202609(-en).png
使い方: python scripts/reins_market_watch_202609.py
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reinfolib import ROOT
from summarize_mansion import BG, GRID, INK, SUB, setup_font

OUT_DIR = ROOT / "public" / "images" / "blog"
NAVY, GOLD = "#4a55a2", "#a07d22"
SOURCE = "出典：東日本不動産流通機構「Market Watch 2026年9月度」中古マンション成約状況"
SOURCE_EN = 'Source: East Japan REINS, "Market Watch", September 2026'

MONTHS = ["25/9", "10", "11", "12", "26/1", "2", "3", "4", "5", "6", "7", "8", "9"]
MONTHS_EN = ["9/25", "10", "11", "12", "1/26", "2", "3", "4", "5", "6", "7", "8", "9"]
KUBU_UNIT = [131.54, 135.03, 130.96, 135.61, 137.50, 133.37, 136.10, 137.46, 131.24, 131.15, 135.77, 132.69, 130.39]
# 都区部の成約件数（都心3区・城東・城南・城西・城北）
TOSHIN = [290, 298, 239, 256, 194, 243, 280, 238, 198, 223, 228, 154, 176]
KUBU_N = [1995, 1836, 1853, 1695, 1433, 1817, 2145, 1635, 1452, 1716, 1509, 1265, 1385]
YOKOHAMA_UNIT = [62.91, 61.87, 62.17, 63.76, 66.48, 64.97, 64.89, 66.84, 61.35, 62.32, 61.99, 62.90, 63.58]
YOKOHAMA_AGE = [28.24, 28.65, 28.29, 28.73, 27.53, 28.25, 28.69, 28.53, 30.36, 29.78, 30.34, 29.50, 30.46]
KAWASAKI_UNIT = [72.08, 74.92, 77.09, 76.72, 77.43, 75.47, 74.91, 77.82, 78.46, 78.01, 74.18, 72.02, 72.19]
KAWASAKI_AGE = [23.65, 24.25, 24.78, 25.67, 24.01, 25.49, 25.42, 25.24, 25.12, 24.45, 25.47, 26.85, 26.72]


def panel(ax, months, title, series, ylim, fmt, marks):
    """series: [(値のリスト, 色, 凡例)]、marks: 数値を添える月の位置。"""
    x = range(len(months))
    ax.set_facecolor(BG)
    for ys, color, label in series:
        ax.plot(x, ys, color=color, linewidth=2.2, marker="o", markersize=4, label=label)
        for i in marks:
            ax.plot(i, ys[i], "o", color=color, markersize=7)
            # 隣の月より低い点は下に、それ以外は上に数値を置いて線と重ねない
            near = [ys[j] for j in (i - 1, i + 1) if 0 <= j < len(ys)]
            below = all(v > ys[i] for v in near)
            ax.annotate(fmt(ys[i]), (i, ys[i]), xytext=(0, -10 if below else 9), textcoords="offset points",
                        ha="center", va="top" if below else "bottom", color=INK, fontsize=10.5, fontweight="bold")
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK, pad=14)
    ax.set_xticks(list(x), months)
    ax.set_xlim(-0.3, len(months) - 0.7)
    ax.set_ylim(*ylim)
    ax.grid(axis="y", color=GRID)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=SUB, labelsize=9.5, length=0)
    if len(series) > 1:
        ax.legend(loc="upper left", frameon=False, fontsize=10.5, labelcolor=INK, ncol=2)


def figure(name, months, title, sub, note, left, right):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6.75), dpi=100)
    fig.patch.set_facecolor(BG)
    panel(ax1, months, *left)
    panel(ax2, months, *right)
    fig.text(0.05, 0.92, title, fontsize=19, fontweight="bold", color=INK)
    fig.text(0.05, 0.875, sub, fontsize=10.5, color=SUB)
    fig.text(0.05, 0.07, note, fontsize=10, color=INK, linespacing=1.6)
    fig.text(0.95, 0.03, "katohpm.com", fontsize=10, color=SUB, ha="right")
    fig.subplots_adjust(left=0.06, right=0.95, top=0.76, bottom=0.2, wspace=0.18)
    path = OUT_DIR / name
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    setup_font()
    share = [t / n * 100 for t, n in zip(TOSHIN, KUBU_N)]
    print("都心3区の割合", [round(s, 1) for s in share])
    last, aug = len(MONTHS) - 1, len(MONTHS) - 2

    f2 = lambda v: f"{v:.2f}"
    f1 = lambda v: f"{v:.1f}"
    texts = {
        "ja": dict(
            months=MONTHS, suffix="",
            t1="東京都区部 中古マンション成約：㎡単価と都心3区の割合（月次）",
            s1=f"2025年9月〜2026年9月。{SOURCE}（都区部・地区別）",
            n1="8月は都心3区の割合が12.2%と13か月で最も低く、都区部の㎡単価は前年同月比−0.3%（76か月ぶりの前年割れ）。\n"
               "都心3区の割合＝都心3区（千代田・中央・港）の成約件数÷都区部の成約件数。当社算出。",
            unit="成約㎡単価（万円）", share="都心3区の割合（%）", age="平均築年数（年）",
            t2="横浜市・川崎市 中古マンション成約：㎡単価と平均築年数（月次）",
            s2=f"2025年9月〜2026年9月。{SOURCE}（横浜市・川崎市）",
            n2="9月の㎡単価は前年同月比で横浜市＋1.1%、川崎市＋0.1%。同じ1年で平均築年数は横浜市が＋2.22年、川崎市が＋3.07年古くなっています。",
            kawasaki="川崎市", yokohama="横浜市"),
        "en": dict(
            months=MONTHS_EN, suffix="-en",
            t1="Tokyo 23 wards resale condos: price per m² and central-3-ward share",
            s1=f"Monthly, September 2025 to September 2026. {SOURCE_EN}",
            n1="In August the central 3 wards' share hit a 13-month low of 12.2%, and the 23-ward price per m² fell 0.3% year on year (first fall in 76 months).\n"
               "Central-3-ward share = closed transactions in Chiyoda, Chuo and Minato ÷ all 23 wards. Our calculation.",
            unit="Price per m² (¥10,000)", share="Central 3 wards' share (%)", age="Average building age (years)",
            t2="Yokohama and Kawasaki resale condos: price per m² and building age",
            s2=f"Monthly, September 2025 to September 2026. {SOURCE_EN}",
            n2="September price per m² year on year: Yokohama +1.1%, Kawasaki +0.1%. Over the same year, average building age rose 2.22 years in Yokohama and 3.07 in Kawasaki.",
            kawasaki="Kawasaki", yokohama="Yokohama"),
    }
    for t in texts.values():
        print(figure(
            f"tokyo23ku-mansion-202609{t['suffix']}.png", t["months"], t["t1"], t["s1"], t["n1"],
            (t["unit"], [(KUBU_UNIT, NAVY, "")], (126, 140), f2, (0, aug, last)),
            (t["share"], [(share, GOLD, "")], (10, 18), f1, (0, aug, last)),
        ).relative_to(ROOT))
        print(figure(
            f"yokohama-kawasaki-mansion-202609{t['suffix']}.png", t["months"], t["t2"], t["s2"], t["n2"],
            (t["unit"], [(KAWASAKI_UNIT, NAVY, t["kawasaki"]), (YOKOHAMA_UNIT, GOLD, t["yokohama"])], (58, 82), f2, (0, last)),
            (t["age"], [(KAWASAKI_AGE, NAVY, t["kawasaki"]), (YOKOHAMA_AGE, GOLD, t["yokohama"])], (22, 32), f2, (0, last)),
        ).relative_to(ROOT))

if __name__ == "__main__":
    main()
