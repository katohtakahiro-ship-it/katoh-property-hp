"""不動産情報ライブラリ XIT001 から一都3県の中古マンション成約価格を四半期ごとに取得する。

出力: data/reinfolib/mansion_{都県コード}_{年}Q{四半期}.csv（取得済みは飛ばす。--refresh で再取得）
使い方: python scripts/fetch_transactions.py [--refresh]
"""

import csv
import sys
import urllib.error
from datetime import date
from pathlib import Path

from reinfolib import ROOT, get

OUT_DIR = ROOT / "data" / "reinfolib"
FIRST = (2021, 1)  # 成約価格情報が提供されている最初の四半期
PREFS = {"11": "埼玉県", "12": "千葉県", "13": "東京都", "14": "神奈川県"}
FIELDS = [
    "Period", "MunicipalityCode", "Municipality", "DistrictCode", "DistrictName",
    "TradePrice", "Area", "FloorPlan", "BuildingYear", "Structure", "CityPlanning", "Renovation",
]


def quarters():
    y, q = FIRST
    today = date.today()
    while (y, q) <= (today.year, (today.month - 1) // 3 + 1):
        yield y, q
        y, q = (y + 1, 1) if q == 4 else (y, q + 1)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    refresh = "--refresh" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for y, q in quarters():
        for pref, name in PREFS.items():
            path = OUT_DIR / f"mansion_{pref}_{y}Q{q}.csv"
            if path.exists() and not refresh:
                continue
            try:
                data = get("XIT001", year=y, quarter=q, area=pref, priceClassification="02").get("data", [])
            except urllib.error.HTTPError as e:
                if e.code == 404:  # まだ公表されていない四半期
                    print(f"{y}Q{q}: 未公表")
                    return
                raise
            rows = [{k: r.get(k, "") for k in FIELDS} for r in data if r.get("Type") == "中古マンション等"]
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(rows)
            print(f"{y}Q{q} {name}: {len(rows)} 件 → {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
