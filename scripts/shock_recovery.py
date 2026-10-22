"""リーマンショックとコロナショックで、地価・中古マンション・一戸建ての価格がいつ底を打ち、
何年でリーマンショック前（2008年）の水準に戻ったかを見るためのデータを作り、グラフを描く。
地域は全国・東京都・神奈川県・横浜市・川崎市。どの地域も同じデータ・同じ計算方法で出す。

土地: 地価公示（国土数値情報 L01、2026年版）の住宅地。各地点の前年比のうち「継続」の地点だけを平均し、
      年ごとにつないだ指数（2008年＝100）。国交省の平均変動率と同じ考え方。
マンション: 不動産取引価格情報（不動産情報ライブラリ XIT001）の中古マンション等。
      log(㎡単価) を築年数・専有面積・半期・市区町村で説明するヘドニック指数（2008年上期＝100）。
一戸建て: 同じく宅地（土地と建物）のうち住宅。log(価格) を土地面積・延床面積・築年数・半期・市区町村で
      説明するヘドニック指数（2008年上期＝100）。

使い方:
  python scripts/shock_recovery.py --build L01_GEOJSON_DIR TORIHIKI_DIR   # data/shock_recovery/*.csv を作る
  python scripts/shock_recovery.py                                       # CSV からグラフを描く
    L01_GEOJSON_DIR: L01-26_{01..47}.geojson を置いたフォルダ
    TORIHIKI_DIR:    pref_{01..47}.csv（XIT001 を area=都道府県で 2005年第3四半期〜2025年第4四半期に取得し、
                     中古マンション等と宅地（土地と建物）を残したもの）
出力: public/images/blog/shock-recovery-{chika,mansion,kodate}(-en).png
"""

import csv
import glob
import json
import math
import re
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reinfolib import ROOT
from summarize_mansion import BG, GRID, INK, SUB, setup_font

DATA = ROOT / "data" / "shock_recovery"
OUT_DIR = ROOT / "public" / "images" / "blog"
AREAS = {
    "全国": lambda c: True,
    "東京都": lambda c: c[:2] == "13",
    "神奈川県": lambda c: c[:2] == "14",
    "横浜市": lambda c: "14101" <= c <= "14118",
    "川崎市": lambda c: "14131" <= c <= "14137",
}
COLORS = {"全国": "#9a9a9a", "東京都": "#1a1a2e", "神奈川県": "#5e8c7a", "横浜市": "#a07d22", "川崎市": "#4a55a2"}
SHOCKS = [(2008.7, 2009.5), (2020.2, 2020.6)]  # リーマンショック、コロナショック
# 親族間・古家付き土地など、住宅としての価格を表さない取引を除く
EXCLUDE_REMARKS = ("関係者", "親族", "古屋", "古家", "取り壊し", "隣地", "調停", "競売")
L01_FIRST_YEAR = 1983  # L01_062 が1983年の価格、L01_106 が1984年の前年からの変化（先頭1文字が 1＝継続）


def build_land(geo_dir):
    ratios = defaultdict(list)
    for path in glob.glob(f"{geo_dir}/*.geojson"):
        for feat in json.load(open(path, encoding="utf-8"))["features"]:
            p = feat["properties"]
            if p["L01_002"] != "000":  # 住宅地
                continue
            areas = [a for a, fn in AREAS.items() if fn(p["L01_001"])]
            for i, year in enumerate(range(L01_FIRST_YEAR + 1, 2027)):
                prev, cur = p[f"L01_{62 + i:03d}"], p[f"L01_{63 + i:03d}"]
                if prev and cur and p[f"L01_{106 + i:03d}"][0] == "1":
                    for a in areas:
                        ratios[(a, year)].append(cur / prev)
    rows = []
    for a in AREAS:
        idx, series = 100.0, {L01_FIRST_YEAR: 100.0}
        for year in range(L01_FIRST_YEAR + 1, 2027):
            r = ratios[(a, year)]
            idx *= sum(r) / len(r)
            series[year] = idx
        base = series[2008]
        rows += [[a, y, round(v / base * 100, 2), len(ratios[(a, y)])] for y, v in series.items() if y >= 2005]
    write(DATA / "land_index.csv", ["area", "year", "index_2008", "points"], rows)


def hedonic(x, y, period, ward):
    """log価格 y を、説明変数 x と半期・市区町村の固定効果で回帰し、半期ごとの水準を返す。

    市区町村が全国で約1,900あるため、固定効果は交互に平均を引く方法（alternating projections）で
    取り除いてから x の係数を求め、残差から半期の効果を取り出す。
    """
    import numpy as np

    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    pc, pi = np.unique(period, return_inverse=True)
    wc, wi = np.unique(ward, return_inverse=True)
    np_, nw = np.bincount(pi), np.bincount(wi)

    def demean(v):
        v = v.copy()
        for _ in range(200):
            v -= (np.bincount(wi, v, len(wc)) / nw)[wi]
            step = (np.bincount(pi, v, len(pc)) / np_)[pi]
            v -= step
            if np.abs(step).max() < 1e-9:
                break
        return v

    xd = np.column_stack([demean(x[:, j]) for j in range(x.shape[1])])
    beta = np.linalg.lstsq(xd, demean(y), rcond=None)[0]
    r = y - x @ beta
    pe, we = np.zeros(len(pc)), np.zeros(len(wc))
    for _ in range(500):
        we = np.bincount(wi, r - pe[pi], len(wc)) / nw
        new = np.bincount(pi, r - we[wi], len(pc)) / np_
        done = np.abs(new - pe).max() < 1e-10
        pe = new
        if done:
            break
    return {p: (math.exp(v), int(n)) for p, v, n in zip(pc, pe, np_)}


def build_index(torihiki_dir, kind):
    """kind: "condo"（中古マンション等）または "house"（宅地（土地と建物）のうち住宅）。"""
    recs = []
    for path in sorted(glob.glob(f"{torihiki_dir}/pref_*.csv")):
        for r in csv.DictReader(open(path, encoding="utf-8")):
            m = re.match(r"(\d{4})年", r["BuildingYear"])
            year = int(r["Period"][:4])
            if not m or year > 2025:
                continue
            half = 1 if int(re.search(r"第(\d)", r["Period"]).group(1)) <= 2 else 2
            age = year - int(m.group(1))
            try:
                price = int(r["TradePrice"])
                if kind == "condo":
                    if r["Type"] != "中古マンション等":
                        continue
                    floor = float(r["Area"])
                    if not 15 <= floor <= 200:
                        continue
                    x, logp = (max(0, age), max(0, age) ** 2 / 100, math.log(floor)), math.log(price / floor)
                else:
                    if (r["Type"] != "宅地(土地と建物)" or "住宅" not in r["Use"]
                            or any(w in r["Remarks"] for w in EXCLUDE_REMARKS)):
                        continue
                    land, floor = float(r["Area"]), float(r["TotalFloorArea"])
                    if not (0 <= age <= 50 and 40 <= land <= 400 and 40 <= floor <= 300):
                        continue
                    x, logp = (math.log(land), math.log(floor), age, age * age / 100), math.log(price)
            except ValueError:
                continue  # 「2000㎡以上」など数値でない面積・価格
            recs.append((f"{year}H{half}", r["MunicipalityCode"], x, logp))
    rows = []
    for a, fn in AREAS.items():
        sub = [rec for rec in recs if fn(rec[1])]
        level = hedonic([s[2] for s in sub], [s[3] for s in sub], [s[0] for s in sub], [s[1] for s in sub])
        base = level["2008H1"][0]
        rows += [[a, p, round(v / base * 100, 2), n] for p, (v, n) in sorted(level.items())]
        print(a, len(sub))
    write(DATA / f"{kind}_index.csv", ["area", "period", "index_2008H1", "transactions"], rows)


def write(path, header, rows):
    DATA.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(path.relative_to(ROOT))


def load(name, key, value):
    series = defaultdict(dict)
    for r in csv.DictReader((DATA / name).open(encoding="utf-8")):
        series[r["area"]][r[key]] = float(r[value])
    return series


NAMES_EN = {"全国": "Japan", "東京都": "Tokyo", "神奈川県": "Kanagawa", "横浜市": "Yokohama", "川崎市": "Kawasaki"}
TEXT = {
    "ja": {
        "suffix": "",
        "shocks": ["リーマン\nショック", "コロナ\nショック"],
        "year": "{}年",
        "land": (
            "住宅地の地価：2008年＝100とした推移（地価公示）",
            "2007〜2026年（各年1月1日時点）。出典：国土交通省「地価公示」（国土数値情報 L01）をもとに当社集計",
            "継続して調査されている住宅地の地点について、前年からの変動率の平均を年ごとにつないだ指数です。\n"
            "地価公示は1月1日時点の鑑定評価のため、市況の変化は実際の取引より遅れて表れます。",
            "指数（2008年＝100）"),
        "half_sub": "2007年上期〜2025年下期。出典：国土交通省 不動産情報ライブラリ（不動産取引価格情報）をもとに当社集計",
        "half_ylabel": "指数（2008年上期＝100）",
        "condo": (
            "中古マンションの価格：2008年上期＝100とした推移（半期）",
            "取引価格情報の中古マンション等について、築年数・専有面積・市区町村の違いをそろえた当社推計の指数です。\n"
            "東京都・神奈川県・横浜市・川崎市とも同じ方法で計算しています。"),
        "house": (
            "一戸建ての価格：2008年上期＝100とした推移（半期）",
            "取引価格情報の宅地（土地と建物）のうち住宅について、土地面積・延床面積・築年数・市区町村の違いをそろえた当社推計の指数です。\n"
            "東京都・神奈川県・横浜市・川崎市とも同じ方法で計算しています。"),
    },
    "en": {
        "suffix": "-en",
        "shocks": ["Global\nfinancial crisis", "COVID-19"],
        "year": "{}",
        "land": (
            "Residential land prices, 2008 = 100 (official land prices)",
            "2007–2026, as of January 1 each year. Source: MLIT Official Land Price Publication (Land Numerical Information L01), "
            "compiled by Katoh Property Management",
            "Chain index of the average year-on-year change at residential survey points that were surveyed continuously.\n"
            "Official land prices are appraisals as of January 1, so market changes appear later than in actual transactions.",
            "Index (2008 = 100)"),
        "half_sub": "First half of 2007 to second half of 2025. Source: MLIT Real Estate Information Library (transaction prices), "
                    "compiled by Katoh Property Management",
        "half_ylabel": "Index (first half of 2008 = 100)",
        "condo": (
            "Resale condominium prices, first half of 2008 = 100 (half-yearly)",
            "Our estimated index for resale condominiums in the transaction price data, adjusted for building age, floor area and municipality.\n"
            "Tokyo, Kanagawa, Yokohama and Kawasaki are all calculated the same way."),
        "house": (
            "Detached house prices, first half of 2008 = 100 (half-yearly)",
            "Our estimated index for residential land-and-building transactions, adjusted for land area, floor area, building age and municipality.\n"
            "Tokyo, Kanagawa, Yokohama and Kawasaki are all calculated the same way."),
    },
}


def frame(t, title, sub, note, ylabel):
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for start, end in SHOCKS:
        ax.axvspan(start, end, color=GRID, alpha=0.8, lw=0)
    ax.grid(axis="y", color=GRID)
    ax.axhline(100, color=SUB, linewidth=1, linestyle=(0, (4, 3)))
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=SUB, labelsize=10, length=0)
    ax.set_ylabel(ylabel, color=SUB, fontsize=10)
    en = t["suffix"] == "-en"
    fig.text(0.05, 0.92, title, fontsize=17 if en else 18, fontweight="bold", color=INK)
    fig.text(0.05, 0.875, sub, fontsize=9 if en else 10, color=SUB)
    fig.text(0.05, 0.035, note, fontsize=8.6 if en else 9, color=SUB, linespacing=1.6)
    fig.text(0.95, 0.035, "katohpm.com", fontsize=10, color=SUB, ha="right")
    fig.subplots_adjust(left=0.07, right=0.93, top=0.8, bottom=0.17)
    return fig, ax


def label_shocks(ax, t, ytop):
    for (start, end), label in zip(SHOCKS, t["shocks"]):
        ax.text((start + end) / 2, ytop, label, ha="center", va="top", fontsize=9.5, color=SUB, linespacing=1.3)


def end_labels(ax, t, points):
    """線の右端に地域名と値を、重ならないよう縦にずらして置く（set_ylim の後に呼ぶ）。"""
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * 0.045
    points = sorted(points, key=lambda p: p[2])
    placed = []
    for name, x, y in points:
        ty = max([y] + [p + gap for p in placed[-1:]])
        placed.append(ty)
        label = NAMES_EN[name] if t["suffix"] else name
        ax.annotate(f"{label} {y:.0f}", (x, y), xytext=(x + 0.4, ty), textcoords="data", va="center",
                    color=COLORS[name], fontsize=10.5, fontweight="bold")


def plot_lines(ax, xs_of, s, names):
    for name in names:
        xs, ys = xs_of(s[name])
        ax.plot(xs, ys, color=COLORS[name], linewidth=2 if name in ("全国", "神奈川県") else 2.6,
                linestyle="--" if name == "神奈川県" else "-", marker="o", markersize=3.5)


def save(fig, name, t):
    path = OUT_DIR / f"{name}{t['suffix']}.png"
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


def draw_land(t, ylim):
    s = load("land_index.csv", "year", "index_2008")
    fig, ax = frame(t, *t["land"])
    years = range(2007, 2027)
    plot_lines(ax, lambda d: (list(years), [d[str(y)] for y in years]), s, COLORS)
    ax.set_xlim(2006.5, 2028.8)
    ax.set_xticks(range(2008, 2027, 2), [t["year"].format(y) for y in range(2008, 2027, 2)])
    ax.set_ylim(*ylim)
    end_labels(ax, t, [(n, 2026, s[n]["2026"]) for n in COLORS])
    label_shocks(ax, t, ylim[1] - 1)
    return save(fig, "shock-recovery-chika", t)


def draw_half(t, kind, out_name, ylim):
    s = load(f"{kind}_index.csv", "period", "index_2008H1")
    pos = lambda p: int(p[:4]) + (0.25 if p.endswith("H1") else 0.75)

    def xs_of(d):
        ps = sorted((p for p in d if p >= "2007"), key=pos)
        return [pos(p) for p in ps], [d[p] for p in ps]

    title, note = t[kind]
    fig, ax = frame(t, title, t["half_sub"], note, t["half_ylabel"])
    # 全国は地方の中心都市の伸びで東京都と並び、説明が要るため、マンション・一戸建てでは描かない
    names = [n for n in COLORS if n != "全国"]
    plot_lines(ax, xs_of, s, names)
    ax.set_xlim(2006.8, 2028.8)
    ax.set_xticks(range(2008, 2026, 2), [t["year"].format(y) for y in range(2008, 2026, 2)])
    ax.set_ylim(*ylim)
    end_labels(ax, t, [(n, 2025.75, s[n]["2025H2"]) for n in names])
    label_shocks(ax, t, ylim[1] - 2)
    return save(fig, out_name, t)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if "--build" in sys.argv:
        geo_dir, torihiki_dir = sys.argv[sys.argv.index("--build") + 1:][:2]
        build_land(geo_dir)
        build_index(torihiki_dir, "condo")
        build_index(torihiki_dir, "house")
    setup_font()
    for t in TEXT.values():
        print(draw_land(t, (80, 125)).relative_to(ROOT))
        print(draw_half(t, "condo", "shock-recovery-mansion", (80, 240)).relative_to(ROOT))
        print(draw_half(t, "house", "shock-recovery-kodate", (75, 140)).relative_to(ROOT))


if __name__ == "__main__":
    main()
