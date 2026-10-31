"""レインズの成約事例の検索結果（PDF、売マンション）を読み取って JSON にする。

レインズ会員画面の「売買物件検索結果（成約）」を PDF で保存したもの（data/reins/*.pdf）を読む。
data/reins/ は .gitignore 済み。個別の事例は公開・コミットしない。社内の分析と本格査定にだけ使う。

出力: data/reins/seiyaku.json
  [{no 物件番号, area 専有面積, addr 所在地, deal 取引態様, price 成約価格(万円), zone 用途地域, unit ㎡単価(万円),
    name 建物名, layout 間取, kanri 管理費(円, なしは0、確認中は null), station 沿線駅・交通, date 成約年月日, built 築年, built_m 築月}]
使い方: python scripts/reins_seiyaku.py
"""
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'reins'

RECORD = re.compile(
    r'(?P<no>\d{12}) 中古マンション (?P<area>[\d.]+) m2 (?P<addr>\S+)\n'
    r'(?P<deal>.*?)(?P<price>[\d,]+) 万円 (?P<zone>\S+) (?P<unit>[\d.]+) 万円\s*(?P<name>.*?)\n'
    r'(?P<kanri>なし|確認中|[\d,]+ 円) [\d.]+ 万円 (?P<station>.*?)\n'
    r'令和 *(?P<ry>\d+) 年 *(?P<m>\d+) 月 *(?P<d>\d+) 日\n'
    r'(?P<by>\d{4}) 年.*?(?P<bm>\d+) 月',
    re.S,
)
LAYOUT = re.compile(r'\s*(ワンルーム|\d+ ?S?[LDKR]+)$')


def parse(text: str):
    text = unicodedata.normalize('NFKC', text)
    # ページの頭とお尻（印刷日時・URL・見出し）を落とす
    text = re.sub(r'\n\d{4}/\d{2}/\d{2} \d{2}:\d{2} REINS IP\nhttps://\S+ \d+/\d+', '', text)
    for part in re.split(r'\n\d{1,3} \n(?=\d{12} )', text)[1:]:
        m = RECORD.match(part)
        if not m:
            print('読み取れない行:', part[:80].replace('\n', ' '), file=sys.stderr)
            continue
        name = m['name'].replace('\n', '')
        lm = LAYOUT.search(name)
        yield {
            'no': m['no'], 'area': float(m['area']), 'addr': m['addr'], 'deal': m['deal'].strip(),
            'price': int(m['price'].replace(',', '')), 'zone': m['zone'], 'unit': float(m['unit']),
            'name': name[:lm.start()].strip() if lm else name.strip(), 'layout': lm[1].replace(' ', '') if lm else '',
            'kanri': 0 if m['kanri'] == 'なし' else None if m['kanri'] == '確認中' else int(m['kanri'].replace(',', '').replace(' 円', '')),
            'station': re.sub(r'\s+', ' ', m['station']).strip(),
            'date': f"{2018 + int(m['ry'])}-{int(m['m']):02d}-{int(m['d']):02d}",
            'built': int(m['by']), 'built_m': int(m['bm']),
        }


TSV = re.compile(
    r'(?P<no>\d{12})\t中古マンション\t(?P<area>[\d.]+)m2\t(?P<addr>[^\t]+)\t(?P<deal>.*?)\t?(?P<price>[\d,]+)万円\t'
    r'(?P<zone>[^\t]+)\t(?P<unit>[\d.]+)万円\t(?P<name>.*?)\t?(?P<layout>ワンルーム|\d+S?[LDKR]+)\t'
    r'(?P<kanri>なし|確認中|[\d,]+円)\t[\d.]+万円\t(?P<station>[^\t]*\t[^\t]*)\t'
    r'令和 *(?P<ry>\d+)年 *(?P<m>\d+)月 *(?P<d>\d+)日\t(?P<by>\d{4})年[^\t]*?(?P<bm>\d+)月'
)


def parse_tsv(path):
    """Chrome でレインズの検索結果一覧（画面）から書き出した TSV（1行1事例、画面の表示順に項目をタブ区切り）"""
    for line in open(path, encoding='utf-8'):
        line = unicodedata.normalize('NFKC', line.rstrip('\n'))
        m = TSV.match(line)
        if not m:
            if line.strip():
                print('読み取れない行:', line[:80], file=sys.stderr)
            continue
        yield {
            'no': m['no'], 'area': float(m['area']), 'addr': m['addr'], 'deal': m['deal'].replace('\t', ' ').strip(),
            'price': int(m['price'].replace(',', '')), 'zone': m['zone'], 'unit': float(m['unit']),
            'name': m['name'].replace('\t', ' ').strip(), 'layout': m['layout'],
            'kanri': 0 if m['kanri'] == 'なし' else None if m['kanri'] == '確認中' else int(m['kanri'].replace(',', '').replace('円', '')),
            'station': re.sub(r'\s+', ' ', m['station']).strip(),
            'date': f"{2018 + int(m['ry'])}-{int(m['m']):02d}-{int(m['d']):02d}",
            'built': int(m['by']), 'built_m': int(m['bm']),
        }


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    recs = {}
    for path in sorted(glob.glob(str(SRC / '*.pdf'))):
        text = '\n'.join(p.extract_text() for p in PdfReader(path).pages)
        for r in parse(text):
            recs[r['no']] = r  # 同じ物件番号は1件にまとめる（PDF の重複）
    for path in sorted(glob.glob(str(SRC / 'list' / '*.tsv'))):
        for r in parse_tsv(path):
            recs[r['no']] = r
    out = SRC / 'seiyaku.json'
    out.write_text(json.dumps(list(recs.values()), ensure_ascii=False, indent=1), encoding='utf-8')
    dates = sorted(r['date'] for r in recs.values())
    print(f'{len(recs)} 件（{dates[0]} 〜 {dates[-1]}）→ {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
