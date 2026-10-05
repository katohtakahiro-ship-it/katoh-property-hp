"""data/reinfolib/ の成約価格を四半期×エリアで集計し、㎡単価の推移グラフを描く。

対象はすべて 2005年以降築の中古マンション（武蔵小杉のタワーマンション群と条件をそろえるため）。
API にはタワマンを判別する項目（階数・総戸数）がないため、エリアは町名で定義する（中低層も含む）。

出力:
  data/mansion_summary.csv  … 四半期×グループの件数・㎡単価中央値・4四半期移動中央値・築年中央値
  public/charts/mansion-unit-price.png / -en.png
使い方: python scripts/summarize_mansion.py
"""

import csv
import math
import re
import statistics
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from reinfolib import ROOT

DATA_DIR = ROOT / "data" / "reinfolib"
SUMMARY = ROOT / "data" / "mansion_summary.csv"
CHART_DIR = ROOT / "public" / "charts"
FONT = "C:/Windows/Fonts/NotoSansJP-VF.ttf"

BUILT_FROM = 2005
WINDOW = 4  # 移動中央値の四半期数

# エリア定義（市区町村コード → 町名）
KOSUGI = {"14133": {"小杉町", "新丸子東", "中丸子", "丸子通", "今井南町"}}
KAWASAKI_STA = {
    "14132": {"大宮町", "中幸町", "堀川町", "南幸町"},
    "14131": {"駅前本町", "砂子", "東田町", "本町", "小川町", "日進町", "宮本町", "宮前町"},
}


def in_area(area):
    return lambda r: r["DistrictName"] in area.get(r["MunicipalityCode"], ())


# (キー, 日本語名, 英語名, 条件, 色, 線種)
GROUPS = [
    ("kawasaki", "川崎市全体", "Kawasaki City (whole city)",
     lambda r: r["Municipality"].startswith("川崎市"), "#8a8a8a", "--"),
    ("kawasaki_sta", "川崎駅周辺", "Kawasaki Station area", in_area(KAWASAKI_STA), "#4a55a2", "-"),
    ("tokyo23", "東京23区", "Tokyo 23 wards",
     lambda r: r["MunicipalityCode"].startswith("131"), "#1a1a2e", ":"),
    ("kosugi", "武蔵小杉駅周辺", "Musashi-Kosugi Station area", in_area(KOSUGI), "#b8912f", "-"),
]

# 線が近いグループの数値ラベルを上下にずらす（ポイント）
LABEL_DY = {"tokyo23": 7, "kosugi": -7}

BG, INK, SUB, GRID = "#faf8f3", "#1a1a2e", "#6b6b6b", "#e6e1d6"


def load():
    rows = []
    for path in sorted(DATA_DIR.glob("mansion_*_*.csv")):
        quarter = path.stem.rsplit("_", 1)[1]
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if not (r["TradePrice"].isdigit() and r["Area"].isdigit()):
                    continue  # 「2000㎡以上」などは除外
                m = re.match(r"(\d{4})年", r["BuildingYear"])
                if not m or int(m.group(1)) < BUILT_FROM:
                    continue
                r["built"] = int(m.group(1))
                r["quarter"] = quarter
                r["unit"] = int(r["TradePrice"]) / int(r["Area"])
                rows.append(r)
    return rows


def summarize(rows):
    by = defaultdict(list)
    for r in rows:
        for key, _ja, _en, cond, _c, _l in GROUPS:
            if cond(r):
                by[(r["quarter"], key)].append(r)
    quarters = sorted({r["quarter"] for r in rows})
    out = []
    for i, q in enumerate(quarters):
        for key, ja, *_ in GROUPS:
            g = by.get((q, key), [])
            window = [r for w in quarters[max(0, i - WINDOW + 1):i + 1] for r in by.get((w, key), [])]
            out.append({
                "quarter": q, "group": key, "label": ja, "count": len(g),
                "median_unit_price_man": round(statistics.median(r["unit"] for r in g) / 1e4, 1) if g else "",
                "rolling_count": len(window) if i >= WINDOW - 1 else "",
                "rolling_median_man": round(statistics.median(r["unit"] for r in window) / 1e4, 1)
                if i >= WINDOW - 1 else "",
                "median_built_year": int(statistics.median(r["built"] for r in g)) if g else "",
            })
    return quarters, out


def setup_font():
    """可変フォントは matplotlib で最細ウェイトになるため、Regular/Bold の固定版を作って登録する。"""
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    cache = ROOT / ".cache" / "fonts"
    cache.mkdir(parents=True, exist_ok=True)
    for weight, style in ((400, "Regular"), (700, "Bold")):
        path = cache / f"NotoSansJP-{style}.ttf"
        if not path.exists():
            font = instantiateVariableFont(TTFont(FONT), {"wght": weight}, updateFontNames=True)
            font.save(path)
        font_manager.fontManager.addfont(str(path))
    plt.rcParams["font.family"] = "Noto Sans JP"


def quarter_label(q, lang):
    return f"{q[:4]}年第{q[-1]}四半期" if lang == "ja" else f"{q[:4]} Q{q[-1]}"


def draw(quarters, summary, lang):
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    shown = quarters[WINDOW - 1:]
    x = list(range(len(shown)))
    for key, ja, en, _cond, color, ls in GROUPS:
        ys = [s["rolling_median_man"] for s in summary if s["group"] == key and s["quarter"] in shown]
        if lang == "en":
            ys = [y / 100 for y in ys]  # 万円 → 百万円
        ax.plot(x, ys, color=color, linestyle=ls, linewidth=2.8 if key == "kosugi" else 2,
                marker="o", markersize=4, label=ja if lang == "ja" else en)
        for i in (0, len(ys) - 1):
            ax.annotate(f"{ys[i]:.1f}" if lang == "ja" else f"¥{ys[i]:.2f}M", (x[i], ys[i]),
                        xytext=(-8 if i == 0 else 8, LABEL_DY.get(key, 0)), textcoords="offset points", va="center",
                        ha="right" if i == 0 else "left", color=color, fontsize=11, fontweight="bold")
    ticks = [i for i, q in enumerate(shown) if q.endswith("Q4")]
    ax.set_xticks(ticks, [f"{shown[i][:4]}年" if lang == "ja" else shown[i][:4] for i in ticks])
    ax.set_xlim(-1.5, len(shown) + 0.5)
    ax.grid(axis="y", color=GRID)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=SUB, labelsize=10, length=0)
    handles, labels = ax.get_legend_handles_labels()  # 描画は下の線から、凡例は上の線から並べる
    ax.legend(handles[::-1], labels[::-1], loc="upper left", frameon=False, fontsize=11.5, labelcolor=INK)

    first, last = shown[0], shown[-1]
    if lang == "ja":
        title = f"武蔵小杉・東京23区・川崎駅周辺・川崎市の中古マンション成約㎡単価（{BUILT_FROM}年以降築、万円）"
        sub = (f"直近4四半期の中央値。{quarter_label(first, lang)}〜{quarter_label(last, lang)}。"
               "出典：国土交通省 不動産情報ライブラリ（成約価格情報）をもとに当社集計")
        note = ("武蔵小杉駅周辺＝中原区 小杉町・新丸子東・中丸子・丸子通・今井南町。川崎駅周辺＝幸区 大宮町・中幸町・堀川町・南幸町、"
                "川崎区 駅前本町・砂子・東田町・本町・小川町・日進町・宮本町・宮前町。\n"
                "いずれもタワーマンション以外を含みます。\n"
                "成約価格・面積は公表時に丸められています（㎡単価＝成約価格÷面積）。横軸の目盛りは各年の第4四半期（その年1年間の値）。")
    else:
        title = f"Resale condo price per ㎡: Musashi-Kosugi, Tokyo 23 wards, Kawasaki Station, Kawasaki City (built {BUILT_FROM}+)"
        sub = (f"Median of the last four quarters, ¥ million. {quarter_label(first, lang)} – {quarter_label(last, lang)}. "
               "Source: MLIT Real Estate Information Library (contract prices), compiled by Katoh Property Management")
        note = ("Musashi-Kosugi Station area = Kosugi-cho, Shinmaruko-higashi, Nakamaruko, Marukodori, Imai-minamicho (Nakahara Ward).\n"
                "Kawasaki Station area = Omiya-cho, Nakasaiwai-cho, Horikawa-cho, Minamisaiwai-cho (Saiwai Ward), "
                "Ekimae-honcho, Isago, Higashida-cho, Honcho,\n"
                "Ogawa-cho, Nisshin-cho, Miyamoto-cho, Miyamae-cho (Kawasaki Ward). "
                "All include non-tower buildings. Prices and areas are rounded in the published data.\n"
                "Year ticks mark Q4 (the value for that calendar year).")
    fig.text(0.04, 0.93, title, fontsize=17 if lang == "ja" else 15.5, fontweight="bold", color=INK)
    fig.text(0.04, 0.885, sub, fontsize=10 if lang == "ja" else 9.5, color=SUB)
    fig.text(0.04, 0.035, note, fontsize=8.8 if lang == "ja" else 8.3, color=SUB, linespacing=1.6)
    fig.text(0.96, 0.215, "katohpm.com", fontsize=10, color=SUB, ha="right")
    fig.subplots_adjust(left=0.08, right=0.93, top=0.83, bottom=0.2)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    path = CHART_DIR / ("mansion-unit-price.png" if lang == "ja" else "mansion-unit-price-en.png")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    quarters, summary = summarize(load())
    with SUMMARY.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    print(SUMMARY.relative_to(ROOT))
    setup_font()
    for lang in ("ja", "en"):
        print(draw(quarters, summary, lang).relative_to(ROOT))
    # 各年（第4四半期時点の4四半期値）と直近を表示
    for s in summary:
        if s["rolling_median_man"] != "" and (s["quarter"].endswith("Q4") or s["quarter"] == quarters[-1]):
            print(s["quarter"], s["label"], s["rolling_count"], s["rolling_median_man"])


if __name__ == "__main__":
    main()
