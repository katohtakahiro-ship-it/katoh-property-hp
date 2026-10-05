"""国交省 不動産情報ライブラリ API の共通処理。

API キーは環境変数 REINFOLIB_API_KEY、なければリポジトリ直下の .env から読む。
接続確認: python scripts/reinfolib.py
"""

import gzip
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://www.reinfolib.mlit.go.jp/ex-api/external"
ROOT = Path(__file__).resolve().parent.parent


def api_key() -> str:
    key = os.environ.get("REINFOLIB_API_KEY")
    if not key:
        env = ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                name, sep, value = line.partition("=")
                if sep and name.strip() == "REINFOLIB_API_KEY":
                    key = value.strip().strip('"').strip("'")
    if not key:
        sys.exit("REINFOLIB_API_KEY が未設定です（.env.example を .env にコピーして設定）")
    return key


def get(endpoint: str, **params) -> dict:
    url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"Ocp-Apim-Subscription-Key": api_key(), "Accept-Encoding": "gzip"},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        body = res.read()
        if res.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
    return json.loads(body)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    # 接続確認：川崎市中原区（14133）の成約価格（priceClassification=02）
    result = get("XIT001", year=2025, quarter=1, city="14133", priceClassification="02")
    rows = result.get("data", [])
    print(f"status={result.get('status')} rows={len(rows)}")
    if rows:
        print(json.dumps(rows[0], ensure_ascii=False, indent=2))
