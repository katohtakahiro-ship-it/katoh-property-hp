"""売却の簡易査定ツール（/sell/satei/）用のデータを作る。東京都・神奈川県の全市区町村。

価格の目安を出すのはマンションだけ。戸建て・土地は用途地域や接道で価格が大きく変わるため本格査定に回し、
ページには市区町村の㎡単価の推移だけを参考に出す。

入力（国交省 不動産情報ライブラリ XIT001）:
- マンション data/reinfolib/mansion_{13,14}_*.csv … 成約価格情報（scripts/fetch_transactions.py）
- 戸建て     data/reinfolib/house_{13,14}_*.csv   … 成約価格情報（scripts/fetch_satei.py）
- 土地       data/reinfolib/land_{13,14}_*.csv    … 取引価格情報（scripts/fetch_satei.py）
マンション名の一覧:
- data/kawasaki_towers.csv、data/yokohama_mansions.csv、data/satei_buildings_extra.csv

出力: public/data/satei/
- index.json … 四半期の一覧、種類ごとの最新四半期、市区町村の一覧（グループ・種類ごとの件数）
- mansion/<市区町村コード>.json … 町名の一覧、時点修正の指数、事例 [四半期番号, 町名番号, 価格(万円), 専有面積, 築年]
- trend_house.json / trend_land.json … {市区町村コード: 四半期ごとの土地1㎡あたりの中央値（5件未満は null）}
- buildings.json … マンション名の一覧 {n: 名前, c: 市区町村コード, d: 町名, y: 竣工年, u: 総戸数, f: 地上階数, k: 5年間の事例数, s: 同じ町・同じ竣工年の別の建物}

時点修正の指数は、その市区町村の専有㎡単価の前4四半期の中央値。件数が20件に満たない四半期は窓を広げ、
市区町村全体で事例が少なければ都県全体の指数を使う。

国のデータには建物名がないため、マンション名は「市区町村・町名・築年」が同じ事例をそのマンションとみなす
（同じ町・同じ年に建った別の建物が含まれることがある。s に一覧にある建物を入れて画面で断る）。
"""
import csv
import glob
import json
import os
import re
import shutil
import statistics
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'reinfolib')
OUT = os.path.join(ROOT, 'public', 'data', 'satei')
PREFS = ('13', '14')
KINDS = ('mansion', 'house', 'land')
MIN_WINDOW = 20  # 指数の1点に使う最低件数
MIN_LOCAL = 80  # これ未満の市区町村は都県の指数を使う
MIN_TREND = 5  # 推移グラフの1点に使う最低件数
# マンション名の一覧。横浜（data/yokohama_mansions.csv、作成済み）は川崎でのテストが終わってから加える
BUILDING_LISTS = (('kawasaki_towers.csv', '川崎市'),)


def num(s: str):
    try:
        return float(s)
    except ValueError:
        return None


def parse_period(s: str) -> str:
    m = re.match(r'(\d{4})年第(\d)四半期', s)
    return f'{m.group(1)}Q{m.group(2)}'


def group_of(code: str) -> str:
    c = int(code)
    if code.startswith('13'):
        if c <= 13123:
            return '東京23区'
        return '東京都 市部' if c < 13300 else '東京都 町村'
    if 14101 <= c <= 14118:
        return '横浜市'
    if 14131 <= c <= 14137:
        return '川崎市'
    if 14151 <= c <= 14153:
        return '相模原市'
    return '神奈川県 市部' if c < 14300 else '神奈川県 町村'


def load(kind: str):
    rows = []
    for pref in PREFS:
        for path in sorted(glob.glob(os.path.join(SRC, f'{kind}_{pref}_*.csv'))):
            with open(path, encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    area = num(r['Area'])
                    price = num(r['TradePrice'])
                    if not area or not price or not r['MunicipalityCode']:
                        continue
                    built = int(r['BuildingYear'][:4]) if r.get('BuildingYear', '')[:4].isdigit() else 0
                    if kind == 'mansion' and not built:
                        continue
                    rows.append({'q': parse_period(r['Period']), 'code': r['MunicipalityCode'], 'name': r['Municipality'],
                                 'district': r['DistrictName'], 'price': price / 10000, 'area': area, 'built': built})
    return rows


def index_series(deals, qi, n):
    """各四半期の㎡単価指数（前4四半期の中央値。件数が足りなければ窓を広げる）"""
    by_q = defaultdict(list)
    for d in deals:
        by_q[qi[d['q']]].append(d['price'] / d['area'])
    out = []
    for i in range(n):
        w = 3
        while True:
            pool = [u for j in range(max(0, i - w), i + 1) for u in by_q.get(j, [])]
            if len(pool) >= MIN_WINDOW or w >= n:
                break
            w += 1
        out.append(round(statistics.median(pool), 3) if pool else None)
    # 先頭に値がない四半期は最初の値で埋める
    first = next((v for v in out if v is not None), 1)
    return [v if v is not None else first for v in out]


def trend(rows, qi, n):
    """市区町村ごとの、四半期別の㎡単価の中央値"""
    by = defaultdict(lambda: defaultdict(list))
    for d in rows:
        by[d['code']][qi[d['q']]].append(d['price'] / d['area'])
    return {code: [round(statistics.median(qs[i]), 1) if len(qs.get(i, [])) >= MIN_TREND else None for i in range(n)]
            for code, qs in by.items()}


def load_buildings(names, mansion_rows):
    """マンション名の一覧を読み、成約事例（市区町村・町名・築年が同じもの）と突き合わせる"""
    code_of = {name: code for code, name in names.items()}
    town = lambda s: re.sub(r'[0-9０-９]+丁目.*$', '', s).strip()
    items = []

    def add(muni, name, address, built, units, floors=''):
        code = code_of.get(muni)
        year = built[:4]
        if not code or not year.isdigit() or not address:
            return
        items.append({'n': name, 'c': code, 'd': town(address), 'y': int(year), 'u': int(units) if units.isdigit() else None,
                      'f': int(floors) if floors.isdigit() else None})

    for path, city in BUILDING_LISTS:
        full = os.path.join(ROOT, 'data', path)
        if not os.path.exists(full):
            continue
        with open(full, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r['状況'] != '竣工' or r['分譲/賃貸'] != '分譲':
                    continue
                add(city + r['区'], r['物件名'], r['所在地'], r['竣工年月'], r['総戸数'], r['地上階数'])
    with open(os.path.join(ROOT, 'data', 'satei_buildings_extra.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            add(r['市区'], r['物件名'], r['所在地'], r['竣工年月'], r['総戸数'], r.get('地上階数', ''))

    count = defaultdict(int)
    for d in mansion_rows:
        count[(d['code'], d['district'], d['built'])] += 1
    # 国のデータの築年は、資料の竣工年と1年ずれることがある（年度・登記の時期の違いとみられる）。
    # 竣工年の事例が10件未満なら、前後1年のうち事例の多い年を使う
    for b in items:
        y = b['y']
        if count[(b['c'], b['d'], y)] < 10:
            y = max((y - 1, y, y + 1), key=lambda v: count[(b['c'], b['d'], v)])
        b['y'] = y
    same = defaultdict(list)
    for b in items:
        same[(b['c'], b['d'], b['y'])].append(b['n'])
    for b in items:
        key = (b['c'], b['d'], b['y'])
        b['k'] = count[key]
        b['s'] = [n for n in same[key] if n != b['n']]
    return sorted(items, key=lambda b: b['n'])


def main():
    data = {k: load(k) for k in KINDS}
    quarters = sorted({d['q'] for rows in data.values() for d in rows})
    qi = {q: i for i, q in enumerate(quarters)}
    n = len(quarters)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'mansion'))
    names, counts = {}, defaultdict(dict)
    last = {k: max(qi[d['q']] for d in rows) for k, rows in data.items()}
    for kind, rows in data.items():
        for d in rows:
            names[d['code']] = d['name']
            counts[d['code']][kind] = counts[d['code']].get(kind, 0) + 1

    rows = data['mansion']
    pref_idx = {p: index_series([d for d in rows if d['code'].startswith(p)], qi, n) for p in PREFS}
    by_code = defaultdict(list)
    for d in rows:
        by_code[d['code']].append(d)
    for code, items in by_code.items():
        districts = sorted({d['district'] for d in items if d['district']})
        di = {d: i for i, d in enumerate(districts)}
        idx = index_series(items, qi, n) if len(items) >= MIN_LOCAL else pref_idx[code[:2]]
        deals = [[qi[d['q']], di.get(d['district'], -1), round(d['price']), round(d['area']), d['built']] for d in items]
        with open(os.path.join(OUT, 'mansion', f'{code}.json'), 'w', encoding='utf-8') as f:
            json.dump({'code': code, 'name': names[code], 'districts': districts, 'idx': idx, 'deals': deals},
                      f, ensure_ascii=False, separators=(',', ':'))

    for kind in ('house', 'land'):
        with open(os.path.join(OUT, f'trend_{kind}.json'), 'w', encoding='utf-8') as f:
            json.dump(trend(data[kind], qi, n), f, ensure_ascii=False, separators=(',', ':'))

    buildings = load_buildings(names, rows)
    with open(os.path.join(OUT, 'buildings.json'), 'w', encoding='utf-8') as f:
        json.dump(buildings, f, ensure_ascii=False, separators=(',', ':'))

    meta = {
        'quarters': quarters,
        'last': last,
        'munis': [{'code': c, 'name': names[c], 'group': group_of(c), 'counts': counts[c]} for c in sorted(names)],
    }
    with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, separators=(',', ':'))
    for kind, rows in data.items():
        print(f'{kind}: {len(rows)} deals, last {quarters[last[kind]]}')
    ok = [b for b in buildings if b['k'] >= 10]
    print(f'buildings: {len(buildings)}, with 10+ deals: {len(ok)}')
    for b in buildings:
        print(f"  {b['k']:4d}  {b['n']}  ({names[b['c']]}{b['d']} {b['y']})" + (f"  同じ町・年: {'、'.join(b['s'])}" if b['s'] else ''))


if __name__ == '__main__':
    main()
