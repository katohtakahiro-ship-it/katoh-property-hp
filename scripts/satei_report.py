"""本格査定レポート（PDF）を作る。

入力: reports/<案件>/input.json（物件・補正・データの絞り込み条件）
出力: reports/<案件>/report.pdf と図（chart_*.png）

公的データ（国交省 成約価格情報、data/reinfolib/mansion_*.csv）から同じマンションとみられる事例を選び、
時点修正（市の㎡単価の4四半期移動平均）と補正をかけて価格を出す。レインズの成約事例・売出中の物件・
管理状況・現地確認の欄は、input.json に値がなければ「本番で記入」の空欄として出す。

reports/ はお客様の情報を含むため .gitignore 済み。コミットしない。
使い方: python scripts/satei_report.py reports/<案件>
"""

import csv
import glob
import json
import re
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from summarize_mansion import setup_font

ROOT = Path(__file__).resolve().parent.parent
INK, GOLD, CREAM, MUTED, LINE = "#1a1a2e", "#c9a84c", "#faf8f3", "#7a7a8a", "#e6dcc0"
COMPANY = "合同会社加藤プロパティマネジメント"
LICENSE = "宅地建物取引業 神奈川県知事（2）第30531号"
ADDRESS = "〒211-0025 神奈川県川崎市中原区木月4-51-1"
AGENT = "宅地建物取引士 加藤隆寛"
TODO = "（本番で記入）"


# ---------- データ ----------

def quarter_of(period: str) -> str:
    m = re.match(r"(\d{4})年第(\d)四半期", period)
    return f"{m.group(1)}Q{m.group(2)}"


def load_deals(cfg):
    pref = cfg["ward_code"][:2]
    rows = []
    for path in sorted(glob.glob(str(ROOT / "data" / "reinfolib" / f"mansion_{pref}_*.csv"))):
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["MunicipalityCode"] != cfg["ward_code"] or not r["Area"].isdigit() or not r["BuildingYear"][:4].isdigit():
                    continue
                rows.append({
                    "q": quarter_of(r["Period"]), "district": r["DistrictName"], "price": int(r["TradePrice"]) / 10000,
                    "area": int(r["Area"]), "built": int(r["BuildingYear"][:4]), "layout": r["FloorPlan"],
                    "renovation": r["Renovation"],
                })
    return rows


def city_index(ward_code: str):
    meta = json.loads((ROOT / "public" / "data" / "satei" / "index.json").read_text(encoding="utf-8"))
    s = meta["index"]["kawasaki" if ward_code >= "14131" else "yokohama"]
    rolled = [statistics.mean(s[max(0, i - 3): i + 1]) for i in range(len(s))]
    return meta["quarters"], rolled


def round10(n: float) -> int:
    return int(round(n / 10) * 10)


def qlabel(q: str) -> str:
    return f"{q[:4]}年{q[-1]}Q"


# ---------- 図 ----------

def chart_comps(complex_deals, comps, quarters, est_unit, out: Path):
    qi = {q: i for i, q in enumerate(quarters)}
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    ax.scatter([qi[d["q"]] for d in complex_deals], [d["price"] / d["area"] for d in complex_deals],
               s=14, color="#c8c8d0", label="パークシティ新川崎 全棟（推定）")
    ax.scatter([qi[d["q"]] for d in comps], [d["price"] / d["area"] for d in comps],
               s=36, color=GOLD, edgecolor=INK, linewidth=0.6, zorder=3, label="1986年築・65㎡前後（I棟・J棟とみられる）")
    ax.axhline(est_unit, color=INK, linestyle="--", linewidth=1)
    ax.text(0, est_unit + 0.6, f"査定 {est_unit:.1f}万円/㎡", va="bottom", ha="left", fontsize=8, color=INK)
    ticks = [i for i, q in enumerate(quarters) if q.endswith("Q1")]
    ax.set_xticks(ticks, [quarters[i][:4] for i in ticks])
    ax.set_ylabel("成約㎡単価（万円/㎡）", fontsize=8)
    ax.tick_params(labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#eee")
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def chart_ward(deals, quarters, ward_name, out: Path):
    by = {q: [] for q in quarters}
    for d in deals:
        by[d["q"]].append(d["price"] / d["area"])
    med = [statistics.median(by[q]) if len(by[q]) >= 5 else None for q in quarters]
    cnt = [len(by[q]) for q in quarters]
    fig, ax = plt.subplots(figsize=(7.2, 2.8), dpi=200)
    ax2 = ax.twinx()
    ax2.bar(range(len(quarters)), cnt, color="#ece6d4", width=0.7)
    ax2.set_ylabel("成約件数", fontsize=8, color=MUTED)
    ax.plot(range(len(quarters)), med, color=GOLD, linewidth=2.2, marker="o", markersize=3)
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    ticks = [i for i, q in enumerate(quarters) if q.endswith("Q1")]
    ax.set_xticks(ticks, [quarters[i][:4] for i in ticks])
    ax.set_ylabel(f"{ward_name} ㎡単価中央値（万円/㎡）", fontsize=8)
    for a in (ax, ax2):
        a.tick_params(labelsize=8)
        a.spines["top"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ---------- PDF ----------

def styles():
    pdfmetrics.registerFont(TTFont("Noto", str(ROOT / ".cache" / "fonts" / "NotoSansJP-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("NotoB", str(ROOT / ".cache" / "fonts" / "NotoSansJP-Bold.ttf")))
    base = ParagraphStyle("base", fontName="Noto", fontSize=9.5, leading=16, textColor=colors.HexColor(INK), wordWrap="CJK")
    return {
        "base": base,
        "small": ParagraphStyle("small", parent=base, fontSize=7.8, leading=12, textColor=colors.HexColor(MUTED)),
        "h1": ParagraphStyle("h1", parent=base, fontName="NotoB", fontSize=22, leading=32),
        "h2": ParagraphStyle("h2", parent=base, fontName="NotoB", fontSize=13.5, leading=20, spaceBefore=4, spaceAfter=8,
                             borderPadding=(0, 0, 0, 6), leftIndent=8, borderColor=colors.HexColor(GOLD), borderWidth=0),
        "h3": ParagraphStyle("h3", parent=base, fontName="NotoB", fontSize=10.5, leading=16, spaceBefore=8, spaceAfter=4),
        "label": ParagraphStyle("label", parent=base, fontSize=8, leading=11, textColor=colors.HexColor(MUTED), alignment=TA_CENTER),
        "big": ParagraphStyle("big", parent=base, fontName="NotoB", fontSize=20, leading=26, alignment=TA_CENTER),
        "cell": ParagraphStyle("cell", parent=base, fontSize=8.5, leading=13),
        "todo": ParagraphStyle("todo", parent=base, fontSize=8.5, leading=13, textColor=colors.HexColor("#b3261e")),
    }


def h2(text, st):
    """左に金色の線を引いた見出し"""
    t = Table([[Paragraph(text, st["h2"])]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("LINEBEFORE", (0, 0), (0, 0), 3, colors.HexColor(GOLD)), ("LEFTPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    return t


def table(rows, widths, st, header=True, todo_cols=()):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), st["todo"] if (c == TODO or (i > 0 and j in todo_cols)) else st["cell"]) for j, c in enumerate(r)])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(LINE)), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(CREAM))]
    t.setStyle(TableStyle(style))
    return t


def main(case_dir: Path):
    cfg = json.loads((case_dir / "input.json").read_text(encoding="utf-8"))
    prop, dcfg = cfg["property"], cfg["data"]
    setup_font()
    st = styles()

    quarters, idx = city_index(dcfg["ward_code"])
    last = len(quarters) - 1
    qi = {q: i for i, q in enumerate(quarters)}
    deals = load_deals(dcfg)
    complex_deals = [d for d in deals if d["district"] == dcfg["district"] and d["built"] in dcfg["complex_years"]]
    if dcfg.get("time_index") == "complex":
        # 大規模マンションは市全体（タワマンが押し上げる）より、そのマンション自身の値動きで時点修正する。
        # 各四半期の前後4四半期（8件に満たなければ広げる）の㎡単価中央値を指数にする
        idx = []
        for i in range(len(quarters)):
            w = 3
            while True:
                pool = [d["price"] / d["area"] for d in complex_deals if i - w <= qi[d["q"]] <= i]
                if len(pool) >= 8 or w >= len(quarters):
                    break
                w += 1
            idx.append(statistics.median(pool))
        time_note = "パークシティ新川崎とみられる全事例の㎡単価（4四半期の移動中央値）"
    else:
        time_note = "川崎市全体の中古マンション㎡単価（4四半期の移動平均）"
    comps = [d for d in complex_deals if d["built"] in dcfg["same_building_years"] and abs(d["area"] - prop["area"]) <= dcfg["area_tolerance"]]
    comps.sort(key=lambda d: d["q"], reverse=True)
    for d in comps:
        d["factor"] = idx[last] / idx[qi[d["q"]]]
        d["adj_unit"] = d["price"] * d["factor"] / d["area"]
    base_unit = statistics.median(d["adj_unit"] for d in comps)
    adj_total = sum(a["rate"] for a in cfg["adjustments"])
    est_unit = base_unit * (1 + adj_total)
    expected = round10(est_unit * prop["area"])
    listing = round10(expected * 1.05)
    quick = round10(expected * 0.94)
    lo = round10(min(d["adj_unit"] for d in comps) * (1 + adj_total) * prop["area"])
    hi = round10(max(d["adj_unit"] for d in comps) * (1 + adj_total) * prop["area"])
    challenge = max(hi, listing)  # 事例の上限。最初の1か月だけ試す価格

    chart_comps(complex_deals, comps, quarters, est_unit, case_dir / "chart_comps.png")
    chart_ward(deals, quarters, "幸区", case_dir / "chart_ward.png")

    story = []
    W = 170 * mm

    # --- 表紙 ---
    story += [Spacer(1, 30 * mm),
              Paragraph("不動産売却 査定報告書", st["h1"]), Spacer(1, 4 * mm),
              Paragraph(prop["name"], ParagraphStyle("pn", parent=st["h3"], fontSize=14, leading=20)),
              Paragraph(f'{prop["floor"]}階 ／ {prop["area"]}㎡ ／ {prop["layout"]}', st["base"]),
              Spacer(1, 18 * mm), Paragraph(cfg["client"], ParagraphStyle("cl", parent=st["h3"], fontSize=13)),
              Spacer(1, 50 * mm),
              Paragraph(f'作成日：{cfg["date"]}', st["base"]), Paragraph(COMPANY, st["h3"]),
              Paragraph(f"{LICENSE}<br/>{ADDRESS}<br/>担当：{AGENT}", st["base"]), Spacer(1, 8 * mm),
              Paragraph("本書は不動産鑑定評価ではありません。宅地建物取引業法第34条の2第2項にもとづき、媒介価格について意見を述べる際の根拠としてお渡しするものです（表現は要確認）。", st["small"])]
    if cfg.get("sample"):
        story.append(Paragraph("このサンプルは国土交通省の公開データだけで作成しています。レインズの成約事例・売出中の物件・管理状況・現地確認の欄は空欄（赤字）で、本番ではここを埋めます。", st["todo"]))
    story.append(PageBreak())

    # --- 1. 結論 ---
    story.append(h2("1. 査定の結論", st))
    big = ParagraphStyle("big4", parent=st["big"], fontSize=16, leading=22)
    gold_big = ParagraphStyle("big4g", parent=big, textColor=colors.HexColor("#8a6d1f"))
    tiers = [("チャレンジ価格", challenge, "売り出しから1か月", big), ("おすすめの売出価格", listing, "2か月目の見直し先", big),
             ("成約が見込める価格", expected, "実際に売れている水準", gold_big), ("早く売りたい場合", quick, "1〜2か月での成約を優先", big)]
    cards = Table([[Paragraph(t[0], st["label"]) for t in tiers], [Paragraph(f"{t[1]:,}万円", t[3]) for t in tiers],
                   [Paragraph(t[2], st["label"]) for t in tiers]], colWidths=[W / 4] * 4)
    cards.setStyle(TableStyle([*[("BOX", (i, 0), (i, -1), 0.6, colors.HexColor(LINE)) for i in range(4)],
                               ("BOX", (2, 0), (2, -1), 1.4, colors.HexColor(GOLD)), ("BACKGROUND", (2, 0), (2, -1), colors.HexColor(CREAM)),
                               ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [cards, Spacer(1, 5 * mm),
              Paragraph(f"同じ時期に建った棟（1986年築、I棟・J棟とみられる）の65㎡前後の成約{len(comps)}件を、{qlabel(quarters[last])}時点の水準に直すと、"
                        f"㎡単価の中央値は{base_unit:.1f}万円でした。これに14階（15階建ての上から2つ目）の補正{adj_total:+.0%}をかけ、"
                        f"㎡単価{est_unit:.1f}万円 × {prop['area']}㎡ ＝ <b>{expected:,}万円</b>を成約が見込める価格としました。"
                        f"事例の範囲から見た幅は {lo:,}万〜{hi:,}万円です。", st["base"]),
              Spacer(1, 3 * mm),
              Paragraph(f"最初の1か月は、事例の上限にあたる<b>{challenge:,}万円</b>で売り出すことをおすすめします。14階の眺望や室内の状態が評価されれば届く水準です。"
                        f"反響が少なければ2か月目に{listing:,}万円へ、3か月目以降は{expected:,}万円を目安に条件を詰めます。最初から安く出す必要はありません。", st["base"]),
              Spacer(1, 6 * mm), h2("2. 物件の概要", st)]
    story.append(table([
        ["項目", "内容"],
        ["物件名", prop["name"]], ["所在地", prop["address"]], ["竣工", prop["built"]], ["構造・規模", prop["structure"]],
        ["総戸数", prop["units"]], ["所在階・専有面積・間取り", f'{prop["floor"]}階 ／ {prop["area"]}㎡ ／ {prop["layout"]}'],
        ["交通", prop["stations"]],
        ["管理費・修繕積立金（月額）", TODO], ["長期修繕計画・大規模修繕の履歴", TODO], ["管理会社・管理形態", "三井不動産レジデンシャルサービス（全部委託）、24時間有人管理"],
        ["登記（権利関係・抵当権）", TODO], ["現地確認（室内・眺望・共用部）", TODO],
    ], [55, 115], st))
    story.append(PageBreak())

    # --- 3. 根拠 ---
    story += [h2("3. 査定の根拠", st), Paragraph("3-1. 同じマンションの成約事例（国土交通省 成約価格情報）", st["h3"]),
              Image(str(case_dir / "chart_comps.png"), width=W, height=W * 3.4 / 7.2),
              Paragraph("国のデータには建物名がないため、幸区小倉・1985〜1988年築の事例をパークシティ新川崎とみなしています（同じ町・同じ年代の別の建物が含まれる可能性があります）。階数・向きはデータにありません。", st["small"]),
              Spacer(1, 3 * mm)]
    rows = [["成約時期", "面積", "間取り", "成約価格", "㎡単価", "時点修正率", "修正後㎡単価"]]
    for d in comps:
        rows.append([qlabel(d["q"]), f'{d["area"]}㎡', d["layout"], f'{d["price"]:,.0f}万円', f'{d["price"] / d["area"]:.1f}万円',
                     f'{d["factor"] - 1:+.1%}', f'{d["adj_unit"]:.1f}万円'])
    rows.append(["", "", "", "", "", "中央値", f"{base_unit:.1f}万円"])
    story += [table(rows, [24, 16, 18, 27, 25, 28, 32], st), Spacer(1, 2 * mm),
              Paragraph(f"時点修正：{time_note}の変化率で、{qlabel(quarters[last])}の水準に直しています。", st["small"]),
              Paragraph("3-2. 補正", st["h3"])]
    arows = [["項目", "補正率", "理由"]] + [[a["item"], f'{a["rate"]:+.0%}', a["note"]] for a in cfg["adjustments"]]
    story += [table(arows, [45, 18, 107], st)]

    story += [KeepTogether([Paragraph("3-3. レインズの成約事例（同じマンション・近くの物件）", st["h3"]),
              table([["成約時期", "棟・階", "向き", "面積", "成約価格", "㎡単価", "売出から成約まで"]] + [[TODO, "", "", "", "", "", ""]] * 4,
                    [30, 20, 14, 16, 28, 24, 38], st)]),
              Paragraph("レインズは不動産会社だけが使える取引情報システムで、棟・階・向き・売出から成約までの期間まで分かります。レポートへの掲載範囲はレインズの利用規程を確認のうえ決めます（要確認）。", st["small"]),
              Paragraph("3-4. いま売り出し中の競合物件", st["h3"]),
              table([["物件", "棟・階", "面積", "売出価格", "㎡単価", "売出期間"]] + [[TODO, "", "", "", "", ""]] * 3, [40, 22, 18, 30, 24, 36], st),
              PageBreak(), h2("4. 市場の動き", st),
              Paragraph("幸区の中古マンション（成約価格）", st["h3"]),
              Image(str(case_dir / "chart_ward.png"), width=W * 0.9, height=W * 0.9 * 2.8 / 7.2)]
    kakaku = ROOT / cfg["kakaku_chart"]
    if kakaku.exists():
        story += [KeepTogether([Paragraph("パークシティ新川崎の20年の価格推移（国土交通省 取引価格情報）", st["h3"]),
                                Image(str(kakaku), width=W * 0.9, height=W * 0.9 * 0.56)])]
    story.append(PageBreak())

    # --- 5. 売却プラン ---
    story += [h2("5. 売却プラン", st), table([
        ["時期", "内容"],
        ["1週目", "媒介契約、室内写真の撮影、販売図面の作成"],
        ["2週目〜1か月目", f"チャレンジ価格（{challenge:,}万円）で売り出し。レインズ登録、ポータルサイト掲載、内見対応（当社が立ち会います）"],
        ["2か月目", f"反響（問い合わせ・内見の数）を見て、おすすめの売出価格（{listing:,}万円）へ見直すかご相談"],
        ["3か月目以降", f"成約が見込める価格（{expected:,}万円）を目安に、購入申込・条件交渉、売買契約（電子契約）"],
        ["契約後1〜2か月", "残代金の受け取り、引き渡し"],
    ], [35, 135], st), Spacer(1, 6 * mm)]

    # --- 6. 手取り ---
    def our_fee(p):
        return (p * 0.015 + 3) * 1.1

    def max_fee(p):
        return (p * 0.03 + 6) * 1.1

    def same_net(p):
        """手数料が法定上限の会社で、当社と同じ手取りを得るのに必要な売却価格"""
        return (p - our_fee(p) + 6.6) / 0.967

    fee = our_fee(expected)
    story += [h2("6. お手取りの試算", st), Paragraph("6-1. 成約が見込める価格で売れた場合", st["h3"]), table([
        ["項目", "金額", "備考"],
        ["売却価格", f"{expected:,}万円", ""],
        ["仲介手数料（当社）", f"−{fee:,.1f}万円", "成約価格の1.5%＋3万円＋消費税"],
        ["抵当権の抹消費用", "−2〜3万円", "登録免許税と司法書士報酬の目安。ローンがない場合は不要"],
        ["住宅ローンの残高", TODO, "金融機関の残高証明で確認"],
        ["お手取り（税金を除く）", f"約{expected - fee - 3:,.0f}万円 − ローン残高", ""],
    ], [45, 45, 80], st),
        Paragraph("ご自宅の売却では、譲渡所得から3,000万円を控除できる特例などがあります。適用できるか、税額がいくらになるかは、税理士・税務署にご確認ください。", st["small"]),
        KeepTogether([
            Paragraph("6-2. 仲介手数料が法定上限の会社との比較", st["h3"]),
            table([["売却価格", "当社の手数料", "法定上限の手数料", "手取りの差", "上限の会社で同じ手取りに必要な価格"]] +
                  [[f"{p:,}万円", f"{our_fee(p):,.1f}万円", f"{max_fee(p):,.1f}万円", f"+{max_fee(p) - our_fee(p):,.1f}万円", f"約{round10(same_net(p)):,}万円"]
                   for p in (challenge, listing, expected, quick)], [27, 30, 33, 28, 52], st),
            Spacer(1, 2 * mm),
            Paragraph(f"成約が見込める価格（{expected:,}万円）で売れた場合、当社なら手数料が上限の会社より約{max_fee(expected) - our_fee(expected):,.0f}万円少なく済みます。"
                      f"同じ手取りを上限の会社で得るには、約{round10(same_net(expected)):,}万円で売る必要があります。手数料はいずれも税込です。", st["base"]),
        ]),
        Spacer(1, 6 * mm), h2("7. 注意事項", st)]
    for t in [
        "本書の価格は、国土交通省の成約価格情報などをもとにした当社の意見で、不動産鑑定士による鑑定評価ではありません。実際の成約価格を保証するものではありません。",
        "国土交通省のデータは、個別の取引が特定されないよう、面積・価格が丸められ、建物名・階数が載っていません。",
        f"出典：国土交通省 不動産情報ライブラリ（成約価格情報 2021年1Q〜{qlabel(quarters[last])}、取引価格情報）。",
        "仲介手数料（法定上限の半額）は、当社サイト・LINE・ご紹介から新規にご相談いただいた場合の料金です。",
    ]:
        story.append(Paragraph("・" + t, st["small"]))

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Noto", 7.5)
        canvas.setFillColor(colors.HexColor(MUTED))
        if doc.page > 1:
            canvas.drawString(20 * mm, 12 * mm, f"{COMPANY}　{LICENSE}")
            canvas.drawRightString(190 * mm, 12 * mm, str(doc.page))
            canvas.setStrokeColor(colors.HexColor(GOLD))
            canvas.setLineWidth(1.2)
            canvas.line(20 * mm, 285 * mm, 190 * mm, 285 * mm)
        else:
            canvas.setFillColor(colors.HexColor(INK))
            canvas.rect(0, 0, 8 * mm, 297 * mm, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor(GOLD))
            canvas.rect(8 * mm, 0, 1.5 * mm, 297 * mm, fill=1, stroke=0)
        if cfg.get("sample"):
            canvas.setFont("NotoB", 70)
            canvas.setFillColor(colors.Color(0.79, 0.66, 0.30, alpha=0.08))
            canvas.translate(105 * mm, 148 * mm)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, "SAMPLE")
        canvas.restoreState()

    out = case_dir / "report.pdf"
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=20 * mm,
                      title=f"査定報告書 {prop['name']}", author=COMPANY).build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(out.relative_to(ROOT), f"comps={len(comps)} base={base_unit:.1f} est={est_unit:.1f} challenge={challenge} listing={listing} expected={expected} quick={quick}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(ROOT / sys.argv[1])
