"""川崎市の区別タワマン棟数（地上20階以上・40階以上）を地図で描く。

背景は国土地理院の地理院タイル（淡色地図、ズーム13）、区の境界は国土数値情報（行政区域データ N03、神奈川県）。
どちらも .cache/ に取得して使い回す（無ければダウンロードする）。棟数は data/kawasaki_towers.csv の竣工済みの行から数える。

出力（日英）:
  public/images/blog/kawasaki-tower-map.png / -en.png        … 20階以上（幸区・中原区を強調）
  public/images/blog/kawasaki-tower-map-20-40.png / -en.png  … 20階以上と40階以上の2段
使い方: python scripts/kawasaki_tower_map.py
"""

import csv
import io
import json
import math
import time
import urllib.request
import zipfile
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image

from reinfolib import ROOT
from summarize_mansion import setup_font

CACHE = ROOT / ".cache"
TILE_DIR = CACHE / "gsi_pale_13"
N03_ZIP = CACHE / "n03" / "N03-20250101_14_GML.zip"
N03_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2025/N03-20250101_14_GML.zip"
TOWERS = ROOT / "data" / "kawasaki_towers.csv"
OUT = ROOT / "public" / "images" / "blog"

Z = 13
CROP = (139.44, 139.845, 35.462, 35.65)  # 西, 東, 南, 北
BG, INK, SUB, GOLD = "#faf8f3", "#1a1a2e", "#6b6b6b", "#c9a84c"
# 重心だと境界や海側に寄る区のラベル位置（経度, 緯度）
LABEL_AT = {"川崎区": (139.725, 35.528), "幸区": (139.689, 35.5415)}

WARD_EN = {"麻生区": "Asao", "多摩区": "Tama", "宮前区": "Miyamae", "高津区": "Takatsu",
           "中原区": "Nakahara", "幸区": "Saiwai", "川崎区": "Kawasaki"}
TEXT = {
    "ja": {
        "unit": "{}棟",
        "a_title": "川崎市でタワマンが一番多いのは幸区",
        "a_sub": "20階以上の棟数　幸区{s}棟・中原区（武蔵小杉）{n}棟",
        "c_title": "数え方で入れ替わる「タワマンが多い区」",
        "c_20": "20階以上　最多は幸区（{}棟）",
        "c_40": "40階以上　最多は中原区（{}棟）",
        "note": "地上20階以上の住宅棟（竣工済み、2026年10月時点）。棟数は加藤プロパティマネジメント調べ",
        "credit": "出典：国土地理院（地理院タイル 淡色地図）、国土数値情報（行政区域データ）を加工して作成",
    },
    "en": {
        "unit": "{}",
        "a_title": "Saiwai has the most tower condos in Kawasaki",
        "a_sub": "Buildings of 20+ floors: Saiwai {s}, Nakahara (Musashikosugi) {n}",
        "c_title": "The ward with the most towers depends on how you count",
        "c_20": "20+ floors: Saiwai has the most ({})",
        "c_40": "40+ floors: Nakahara has the most ({})",
        "note": "Residential buildings of 20+ floors above ground, completed as of October 2026. Counts: Katoh Property Management",
        "credit": "Source: Geospatial Information Authority of Japan (GSI Tiles, pale map) and National Land Numerical Information (administrative boundaries), edited",
    },
}


def counts():
    c20, c40 = Counter(), Counter()
    with TOWERS.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["状況"] != "竣工":
                continue
            c20[r["区"]] += 1
            c40[r["区"]] += int(r["地上階数"]) >= 40
    return {k: c20[k] for k in WARD_EN}, {k: c40[k] for k in WARD_EN}


def tile_xy(lon, lat):
    n = 2 ** Z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


TX0, TY0 = (int(v) for v in tile_xy(CROP[0], CROP[3]))
TX1, TY1 = (int(v) for v in tile_xy(CROP[1], CROP[2]))


def px(lon, lat):
    x, y = tile_xy(lon, lat)
    return (x - TX0) * 256, (y - TY0) * 256


def fetch(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(6):  # 地理院タイルは接続が切れることがあるので再試行する
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            path.write_bytes(urllib.request.urlopen(req, timeout=30).read())
            return
        except OSError:
            time.sleep(1 + attempt)
    raise RuntimeError(f"取得できませんでした: {url}")


def mosaic():
    img = Image.new("RGB", ((TX1 - TX0 + 1) * 256, (TY1 - TY0 + 1) * 256))
    for x in range(TX0, TX1 + 1):
        for y in range(TY0, TY1 + 1):
            path = TILE_DIR / f"{Z}_{x}_{y}.png"
            if not path.exists():
                fetch(f"https://cyberjapandata.gsi.go.jp/xyz/pale/{Z}/{x}/{y}.png", path)
            img.paste(Image.open(path).convert("RGB"), ((x - TX0) * 256, (y - TY0) * 256))
    return img


def wards():
    if not N03_ZIP.exists():
        fetch(N03_URL, N03_ZIP)
    with zipfile.ZipFile(N03_ZIP) as z:
        name = next(n for n in z.namelist() if n.endswith(".geojson"))
        g = json.load(io.TextIOWrapper(z.open(name), encoding="utf-8"))
    out = {}
    for f in g["features"]:
        p = f["properties"]
        if p.get("N03_004") != "川崎市":
            continue
        geom = f["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for poly in polys:
            out.setdefault(p["N03_005"], []).append([px(*c) for c in poly[0]])
    return out


def area(ring):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:]))) / 2


def centroid(ring):
    a = cx = cy = 0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        cr = x0 * y1 - x1 * y0
        a += cr
        cx += (x0 + x1) * cr
        cy += (y0 + y1) * cr
    return cx / (3 * a), cy / (3 * a)


def draw_map(ax, img, W, cnt, his, lang):
    """his: {区名: (塗り色, 文字色)} 強調する区"""
    ax.imshow(img, zorder=0)
    x0, y0 = px(CROP[0], CROP[3])
    x1, y1 = px(CROP[1], CROP[2])
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fc=BG, alpha=0.55, zorder=1))  # 市外を薄く
    for name, rings in W.items():
        fc, alpha = (his[name][0], 0.82) if name in his else ("#ffffff", 0.35)
        for r in rings:
            ax.add_patch(Polygon(r, closed=True, fc=fc, alpha=alpha, ec="none", zorder=2))
            ax.add_patch(Polygon(r, closed=True, fill=False, ec=INK if name in his else "#8a8a8a",
                                 lw=1.6 if name in his else 0.9, zorder=3))
    for name, rings in W.items():
        x, y = px(*LABEL_AT[name]) if name in LABEL_AT else centroid(max(rings, key=area))
        if name in his:
            col, s1, s2 = his[name][1], 13, 30
        elif name in ("幸区", "中原区"):
            col, s1, s2 = INK, 12, 20
        else:
            col, s1, s2 = SUB, 10, 13
        stroke = [] if name in his else [pe.withStroke(linewidth=3, foreground="white")]
        label = name if lang == "ja" else WARD_EN[name]
        ax.annotate(label, (x, y), xytext=(0, s2 * 0.62), textcoords="offset points", ha="center", va="center",
                    fontsize=s1, fontweight="bold", color=col, zorder=5, path_effects=stroke)
        ax.annotate(TEXT[lang]["unit"].format(cnt[name]), (x, y), xytext=(0, -s1 * 0.55), textcoords="offset points",
                    ha="center", va="center", fontsize=s2, fontweight="bold", color=col, zorder=5, path_effects=stroke)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.axis("off")


def map_aspect():
    x0, y0 = px(CROP[0], CROP[3])
    x1, y1 = px(CROP[1], CROP[2])
    return (y1 - y0) / (x1 - x0)


def save(fig, name):
    """地図タイルを含むとフルカラー PNG が数MBになるので、256色に減色して保存する。"""
    buf = io.BytesIO()
    fig.savefig(buf, facecolor=BG, format="png")
    plt.close(fig)
    im = Image.open(buf).convert("RGB")
    im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(OUT / name, optimize=True)


def footer(fig, H, t):
    fig.text(0.05, 0.42 / H, t["note"], fontsize=8, color=SUB)
    fig.text(0.05, 0.18 / H, t["credit"], fontsize=8, color=SUB)


def draw_single(img, W, c20, lang):
    t = TEXT[lang]
    w = 10
    mh = w * 0.96 * map_aspect()
    H = mh + 1.9
    fig = plt.figure(figsize=(w, H), dpi=150, facecolor=BG)
    ax = fig.add_axes([0.02, 0.75 / H, 0.96, mh / H])
    draw_map(ax, img, W, c20, {"幸区": (GOLD, INK), "中原区": (INK, "white")}, lang)
    fig.text(0.05, 1 - 0.55 / H, t["a_title"], fontsize=19, fontweight="bold", color=INK)
    fig.text(0.05, 1 - 0.95 / H, t["a_sub"].format(s=c20["幸区"], n=c20["中原区"]), fontsize=11.5, color=SUB)
    footer(fig, H, t)
    suffix = "" if lang == "ja" else "-en"
    save(fig, f"kawasaki-tower-map{suffix}.png")


def draw_double(img, W, c20, c40, lang):
    t = TEXT[lang]
    w = 10
    mh = w * 0.96 * map_aspect()
    H = mh * 2 + 2.45
    fig = plt.figure(figsize=(w, H), dpi=150, facecolor=BG)
    panels = [(c20, "幸区", GOLD, INK, t["c_20"].format(c20["幸区"])),
              (c40, "中原区", INK, "white", t["c_40"].format(c40["中原区"]))]
    for row, (cnt, hi, fc, tc, title) in enumerate(panels):
        top = H - 1.0 - row * (mh + 0.55)
        fig.text(0.05, (top + 0.05) / H, title, fontsize=14, fontweight="bold", color=INK)
        ax = fig.add_axes([0.02, (top - mh - 0.05) / H, 0.96, mh / H])
        draw_map(ax, img, W, cnt, {hi: (fc, tc)}, lang)
    fig.text(0.05, 1 - 0.5 / H, t["c_title"], fontsize=19, fontweight="bold", color=INK)
    footer(fig, H, t)
    suffix = "" if lang == "ja" else "-en"
    save(fig, f"kawasaki-tower-map-20-40{suffix}.png")


def main():
    setup_font()
    c20, c40 = counts()
    img, W = mosaic(), wards()
    for lang in ("ja", "en"):
        draw_single(img, W, c20, lang)
        draw_double(img, W, c20, c40, lang)
    print("20階以上:", c20)
    print("40階以上:", c40)


if __name__ == "__main__":
    main()
