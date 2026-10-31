"""簡易査定（/sell/satei/）の補正率を、レインズの成約事例で計算する。

国交省の成約価格情報は公表が数か月遅れ、価格も丸められているため、簡易査定の目安は最近の成約より低めに出る。
レインズの成約事例（data/reins/seiyaku.json、図面の所在階は data/reins/zumen.json）を、ページと同じ方法で
計算した目安と比べ、「実際÷目安」の中央値を補正率にする。個別の事例は出力しない。

- general: マンション名を選ばない場合（町名・築年の近い事例で計算）。直近3か月の成約
- building: マンション名を選んだ場合（20階建て未満）。直近6か月
- tower: マンション名を選んだ場合（20階建て以上）。直近6か月。所在階の補正をかける前の、建物の中ほどの階の水準
- floor_slope: タワーの所在階の補正。同じ建物の中で最下階から最上階までの差（建物の中の位置 0〜1 あたり）

出力: public/data/satei/calibration.json
使い方: python scripts/reins_calibrate.py （scripts/reins_seiyaku.py と scripts/satei_data.py の後に実行）
"""
import json
import re
import statistics
import sys
import unicodedata
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SATEI = ROOT / 'public' / 'data' / 'satei'
REINS = ROOT / 'data' / 'reins'
# ページ（src/pages/sell/satei.astro）と同じ定数
RECENT, K, MIN_BUILDING, WANT, MIN_COMPS = 12, 6, 10, 12, 5
TOWER_FLOORS = 20


def norm(s):
    return re.sub(r'[\s・･‧\-ー]', '', unicodedata.normalize('NFKC', s or '').lower().replace('ヶ', 'ケ'))


def quantile(a, p):
    s = sorted(a)
    i = (len(s) - 1) * p
    lo = int(i)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def median(a):
    return quantile(a, 0.5)


class Estimator:
    """ページの valueMansion() と同じ計算で、補正前の㎡単価の目安を出す"""

    def __init__(self):
        meta = json.loads((SATEI / 'index.json').read_text(encoding='utf-8'))
        self.code_of = {m['name']: m['code'] for m in meta['munis']}
        self.last = meta['last']['mansion']
        self.buildings = [(norm(b['n']), b) for b in json.loads((SATEI / 'buildings.json').read_text(encoding='utf-8'))]
        self.cache = {}

    def data(self, code):
        if code not in self.cache:
            self.cache[code] = json.loads((SATEI / 'mansion' / f'{code}.json').read_text(encoding='utf-8'))
        return self.cache[code]

    def building(self, name):
        n = norm(name)
        for k, b in self.buildings:
            if k == n:
                return b
        for k, b in self.buildings:
            if len(n) >= 6 and (k.startswith(n) or n.startswith(k)):
                return b
        return None

    def estimate(self, r):
        m = re.match(r'神奈川県(川崎市\S+?区)(.*)$', r['addr'])
        if not m or m[1] not in self.code_of:
            return None, None, None
        d = self.data(self.code_of[m[1]])
        town = re.sub(r'[0-9]+丁目.*$', '', m[2])
        A, B, last = r['area'], r['built'], self.last
        unit = lambda x: x[2] * d['idx'][last] / d['idx'][x[0]] / x[3]
        recent = lambda x: x[0] > last - RECENT
        b = self.building(r['name'])
        if b and b['c'] == d['code']:
            di = d['districts'].index(b['d'])
            own = [x for x in d['deals'] if x[1] == di and x[4] == b['y'] and recent(x)]
            near = [x for x in own if abs(x[3] - A) <= A * 0.3]
            use = near if len(near) >= MIN_BUILDING else own
            if len(own) >= MIN_BUILDING:
                return median([unit(x) for x in use]), 'building', b
            others = lambda x: not (x[1] == di and x[4] == b['y'])
            like = lambda x, at, bt: recent(x) and abs(x[3] - A) <= A * at and abs(x[4] - b['y']) <= bt
            sim = [x for x in d['deals'] if others(x) and x[1] == di and like(x, 0.3, 5)]
            if len(sim) < MIN_BUILDING:
                sim = [x for x in d['deals'] if others(x) and like(x, 0.3, 5)]
            if len(sim) < MIN_BUILDING:
                sim = [x for x in d['deals'] if others(x) and like(x, 0.4, 8)]
            su, ou = [unit(x) for x in sim], [unit(x) for x in use]
            if not su and not ou:
                return None, None, None
            n = len(ou)
            center = (n * median(ou) + K * median(su)) / (n + K) if n and su else median(su or ou)
            return center, 'building', b
        match = lambda x, q, at, bt: x[0] > last - q and abs(x[3] - A) <= A * at and abs(x[4] - B) <= bt
        comps = [x for x in d['deals'] if match(x, 8, 0.25, 7)]
        if len(comps) < WANT:
            comps = [x for x in d['deals'] if match(x, RECENT, 0.25, 7)]
        if len(comps) < WANT:
            comps = [x for x in d['deals'] if match(x, RECENT, 0.35, 12)]
        if len(comps) < MIN_COMPS:
            return None, None, None
        di = d['districts'].index(town) if town in d['districts'] else -1
        u = [unit(x) for x in comps]
        du = [unit(x) for x in comps if x[1] == di] if di >= 0 else []
        return ((len(du) * median(du) + K * median(u)) / (len(du) + K) if du else median(u)), 'general', None


def floor_slope(rows):
    """同じ建物の中で、所在階の位置（0〜1）と「実際÷目安」の関係（建物ごとの中央値からのずれ）"""
    groups = defaultdict(list)
    for x in rows:
        groups[x['b']].append(x)
    dx, dy = [], []
    for v in groups.values():
        if len(v) < 3:
            continue
        mr, mp = median([x['ratio'] for x in v]), statistics.mean(x['pos'] for x in v)
        for x in v:
            dx.append(x['pos'] - mp)
            dy.append(x['ratio'] / mr - 1)
    return sum(a * c for a, c in zip(dx, dy)) / sum(a * a for a in dx), len(dx)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    est = Estimator()
    recs = json.loads((REINS / 'seiyaku.json').read_text(encoding='utf-8'))
    zumen = json.loads((REINS / 'zumen.json').read_text(encoding='utf-8'))
    latest = max(r['date'] for r in recs)
    end = date.fromisoformat(latest)
    since3, since6 = (end - timedelta(days=91)).isoformat(), (end - timedelta(days=183)).isoformat()

    general, building, tower = [], [], []
    for r in recs:
        if r['date'] <= since6:
            continue
        e, mode, b = est.estimate(r)
        if not e:
            continue
        ratio = r['unit'] / e
        if mode == 'general':
            if r['date'] > since3:
                general.append(ratio)
        elif (b['f'] or 0) >= TOWER_FLOORS:
            z = zumen.get(r['no'], {})
            pos = min(z['floor'] / z['floors_total'], 1) if z.get('floor') and z.get('floors_total') else None
            tower.append({'ratio': ratio, 'pos': pos, 'b': b['n']})
        else:
            building.append(ratio)

    slope, n_slope = floor_slope([x for x in tower if x['pos'] is not None])
    # タワーの補正率は、所在階の補正を外した中ほどの階の水準にそろえる
    tower_mid = [x['ratio'] / (1 + slope * (x['pos'] - 0.5)) if x['pos'] is not None else x['ratio'] for x in tower]
    out = {
        'asof': latest,
        'general': round(median(general), 3),
        'building': round(median(building), 3) if len(building) >= 10 else round(median(general), 3),
        'tower': round(median(tower_mid), 3),
        'floor_slope': round(slope, 3),
        'counts': {'general': len(general), 'building': len(building), 'tower': len(tower), 'floor_slope': n_slope},
        'window': {'general': [since3, latest], 'building': [since6, latest]},
    }
    (SATEI / 'calibration.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    main()
