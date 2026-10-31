"""簡易査定（/sell/satei/）用に、戸建てと土地の取引データを不動産情報ライブラリ XIT001 から取得する。

- 戸建て: 成約価格情報（priceClassification=02）の「宅地(土地と建物)」
- 土地:   取引価格情報（priceClassification=01）の「宅地(土地)」。成約価格情報には土地だけの取引が含まれない
マンションは scripts/fetch_transactions.py が取得する data/reinfolib/mansion_*.csv を使う。

出力: data/reinfolib/house_{都県コード}_{年}Q{四半期}.csv、land_{都県コード}_{年}Q{四半期}.csv（取得済みは飛ばす。--refresh で再取得）
使い方: python scripts/fetch_satei.py [--refresh]
"""

import csv
import sys
import urllib.error

from fetch_transactions import quarters
from reinfolib import ROOT, get

OUT_DIR = ROOT / "data" / "reinfolib"
PREFS = {"13": "東京都", "14": "神奈川県"}
KINDS = {
    "house": ("02", "宅地(土地と建物)"),
    "land": ("01", "宅地(土地)"),
}
FIELDS = [
    "Period", "MunicipalityCode", "Municipality", "DistrictCode", "DistrictName", "TradePrice", "Area",
    "TotalFloorArea", "BuildingYear", "Structure", "LandShape", "Frontage", "Direction", "Classification",
    "Breadth", "CityPlanning", "CoverageRatio", "FloorAreaRatio",
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    refresh = "--refresh" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for kind, (price_class, type_name) in KINDS.items():
        for y, q in quarters():
            stop = False
            for pref, name in PREFS.items():
                path = OUT_DIR / f"{kind}_{pref}_{y}Q{q}.csv"
                if path.exists() and not refresh:
                    continue
                try:
                    data = get("XIT001", year=y, quarter=q, area=pref, priceClassification=price_class).get("data", [])
                except urllib.error.HTTPError as e:
                    if e.code == 404:  # まだ公表されていない四半期
                        print(f"{kind} {y}Q{q}: 未公表")
                        stop = True
                        break
                    raise
                rows = [{k: r.get(k, "") for k in FIELDS} for r in data if r.get("Type") == type_name]
                with path.open("w", encoding="utf-8", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=FIELDS)
                    w.writeheader()
                    w.writerows(rows)
                print(f"{kind} {y}Q{q} {name}: {len(rows)} 件")
            if stop:
                break


if __name__ == "__main__":
    main()
