"""
月次アクセスレポート。GA4 と Search Console から前月のデータを集計し、
Claude に所見を書かせて info@katohpm.com にメールで送る。

GitHub Actions（.github/workflows/monthly-report.yml）で毎月3日に実行する。
Search Console は2〜3日遅れでデータが確定するため、1日ではなく3日に回す。

環境変数:
  GA4_PROPERTY_ID          GA4 のプロパティ ID（数字。測定 ID G-... とは別）
  GSC_SITE_URL             Search Console のプロパティ（既定 sc-domain:katohpm.com）
  GOOGLE_SERVICE_ACCOUNT   サービスアカウントの JSON キー（文字列そのもの）
  ANTHROPIC_API_KEY        所見の生成に使う。未設定なら所見なしで送る
  RESEND_API_KEY           メール送信。未設定なら送らずに HTML を書き出す
  REPORT_TO                送信先（既定 info@katohpm.com）

手元で試す:
  python scripts/monthly_report.py --dry-run           # 送信せず report.html を書き出す
  python scripts/monthly_report.py --month 2026-09     # 対象月を指定
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
from pathlib import Path

import requests
from google.oauth2 import service_account

ROOT = Path(__file__).resolve().parent.parent
SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]
# AI アシスタントからの流入（GEO の効果測定）。sessionSource のホスト名に含まれる文字列
AI_SOURCES = {
    "chatgpt.com": "ChatGPT",
    "chat.openai.com": "ChatGPT",
    "perplexity.ai": "Perplexity",
    "claude.ai": "Claude",
    "gemini.google.com": "Gemini",
    "copilot.microsoft.com": "Copilot",
    "bing.com/chat": "Copilot",
}
MODEL = "claude-opus-5-5"


# ── 期間 ──────────────────────────────────────────────


def month_range(ym: str) -> tuple[dt.date, dt.date]:
    y, m = map(int, ym.split("-"))
    start = dt.date(y, m, 1)
    end = (dt.date(y + (m == 12), m % 12 + 1, 1)) - dt.timedelta(days=1)
    return start, end


def previous_month(today: dt.date) -> str:
    first = today.replace(day=1) - dt.timedelta(days=1)
    return first.strftime("%Y-%m")


# ── GA4 ──────────────────────────────────────────────


class GA4:
    def __init__(self, creds, property_id: str):
        from google.analytics.data_v1beta import BetaAnalyticsDataClient

        self.client = BetaAnalyticsDataClient(credentials=creds)
        self.property = f"properties/{property_id}"

    def run(self, dims, metrics, start, end, limit=20, order_metric=None, dim_filter=None):
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            OrderBy,
            RunReportRequest,
        )

        req = RunReportRequest(
            property=self.property,
            dimensions=[Dimension(name=d) for d in dims],
            metrics=[Metric(name=m) for m in metrics],
            date_ranges=[DateRange(start_date=start.isoformat(), end_date=end.isoformat())],
            limit=limit,
        )
        if order_metric:
            req.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True)]
        if dim_filter:
            req.dimension_filter = dim_filter
        res = self.client.run_report(req)
        rows = []
        for r in res.rows:
            row = {d: v.value for d, v in zip(dims, r.dimension_values)}
            row.update({m: float(v.value) for m, v in zip(metrics, r.metric_values)})
            rows.append(row)
        return rows


def event_filter(name: str):
    from google.analytics.data_v1beta.types import Filter, FilterExpression

    return FilterExpression(
        filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value=name))
    )


def collect_ga4(ga: GA4, start, end, prev_start, prev_end) -> dict:
    totals_m = ["sessions", "totalUsers", "newUsers", "screenPageViews", "engagementRate", "averageSessionDuration"]
    cur = ga.run([], totals_m, start, end, limit=1)
    prev = ga.run([], totals_m, prev_start, prev_end, limit=1)
    leads = ga.run(["eventName"], ["eventCount"], start, end, dim_filter=event_filter("generate_lead"))
    prev_leads = ga.run(["eventName"], ["eventCount"], prev_start, prev_end, dim_filter=event_filter("generate_lead"))

    sources = ga.run(["sessionSource", "sessionMedium"], ["sessions", "engagedSessions"], start, end, limit=25, order_metric="sessions")
    ai = {}
    for s in sources:
        for host, label in AI_SOURCES.items():
            if host in s["sessionSource"]:
                ai[label] = ai.get(label, 0) + s["sessions"]

    data = {
        "totals": cur[0] if cur else {},
        "totals_prev": prev[0] if prev else {},
        "leads": leads[0]["eventCount"] if leads else 0,
        "leads_prev": prev_leads[0]["eventCount"] if prev_leads else 0,
        "channels": ga.run(["sessionDefaultChannelGroup"], ["sessions", "engagedSessions"], start, end, order_metric="sessions"),
        "sources": sources,
        "ai_sources": ai,
        "pages": ga.run(["pagePath", "pageTitle"], ["screenPageViews", "userEngagementDuration"], start, end, limit=25, order_metric="screenPageViews"),
        "landing_pages": ga.run(["landingPage"], ["sessions", "engagementRate"], start, end, limit=15, order_metric="sessions"),
        "countries": ga.run(["country"], ["sessions"], start, end, limit=10, order_metric="sessions"),
        "devices": ga.run(["deviceCategory"], ["sessions"], start, end, order_metric="sessions"),
    }
    # /en/ 配下とそれ以外の閲覧数
    en = sum(p["screenPageViews"] for p in data["pages"] if p["pagePath"].startswith("/en"))
    data["en_share_top_pages"] = en / max(1, sum(p["screenPageViews"] for p in data["pages"]))

    # 問い合わせの経路（GA4 でカスタムディメンション登録済みの場合だけ取れる）
    data["lead_paths"] = {}
    for param in ["landing_page", "last_article", "lead_referrer", "form_page"]:
        try:
            data["lead_paths"][param] = ga.run(
                [f"customEvent:{param}"], ["eventCount"], start, end, limit=10,
                order_metric="eventCount", dim_filter=event_filter("generate_lead"),
            )
        except Exception as e:  # 未登録のディメンションは 400 になる
            data["lead_paths"][param] = f"取得できません（GA4 でカスタムディメンション未登録の可能性）: {type(e).__name__}"
    return data


# ── Search Console ───────────────────────────────────


def collect_gsc(creds, site: str, start, end, prev_start, prev_end) -> dict:
    from googleapiclient.discovery import build

    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    def q(s, e, dims, limit):
        body = {"startDate": s.isoformat(), "endDate": e.isoformat(), "dimensions": dims, "rowLimit": limit}
        rows = svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])
        return [
            {**{d: k for d, k in zip(dims, r.get("keys", []))}, "clicks": r["clicks"], "impressions": r["impressions"], "ctr": r["ctr"], "position": r["position"]}
            for r in rows
        ]

    tot = q(start, end, [], 1)
    tot_prev = q(prev_start, prev_end, [], 1)
    return {
        "totals": tot[0] if tot else {},
        "totals_prev": tot_prev[0] if tot_prev else {},
        "queries": q(start, end, ["query"], 30),
        "pages": q(start, end, ["page"], 15),
    }


# ── 記事一覧（その月に公開した記事を所見に渡す） ──────


def published_posts(start, end) -> list[dict]:
    posts = []
    for f in sorted((ROOT / "src/content/blog/ja").glob("*.md")):
        head = f.read_text(encoding="utf-8").split("---")[1]
        m_date = re.search(r"^date:\s*(\S+)", head, re.M)
        m_title = re.search(r"^title:\s*(.+)$", head, re.M)
        draft = re.search(r"^draft:\s*true", head, re.M)
        if not m_date or draft:
            continue
        d = dt.date.fromisoformat(m_date.group(1)[:10])
        posts.append({"slug": f.stem, "title": m_title.group(1).strip() if m_title else f.stem, "date": d.isoformat(), "this_month": start <= d <= end})
    return posts


# ── 所見（Claude） ───────────────────────────────────

SYSTEM = """あなたは、川崎市の小さな不動産仲介会社「合同会社加藤プロパティマネジメント」(katohpm.com) のウェブ担当アドバイザーです。
毎月のアクセスデータを読み、代表の加藤さんに向けて短い所見を書きます。

会社とサイトの前提:
- 武蔵小杉を中心に川崎市・横浜市。仲介手数料は賃貸・売買とも半額（条件付き）。来店不要。電話番号は載せていない
- サイトの目的は、問い合わせ（フォーム送信 = generate_lead）を増やすこと、ブログ記事の蓄積、GEO（ChatGPT・Perplexity・Gemini・Claude などの AI に引用・推薦されること）
- 日英2言語。英語ページは /en/ 配下
- 記事は H2 に質問文、直後に結論、末尾に FAQ という型で書いている

書き方:
- 日本語。です・ます調。Markdown の見出し（##）と箇条書きを使う
- 構成は「## 今月のまとめ」（3行以内）、「## よかったこと」、「## 気になること」、「## 来月やること」（具体的な行動を3つまで。記事テーマの提案を含めてよい）
- 数字は前月比を添える。データが少ない月は、少ないことを前提に、断定しすぎない
- データにない推測はしない。「無料」という言葉は使わない。法令に関わることは断定せず「要確認」と書く
- 全体で800字程度まで
"""


def write_commentary(payload: dict) -> str | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip())
    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "medium"},
            system=SYSTEM,
            messages=[{"role": "user", "content": "今月のデータです。所見を書いてください。\n\n```json\n" + json.dumps(payload, ensure_ascii=False, indent=1, default=str) + "\n```"}],
        )
    except anthropic.APIError as e:
        print(f"所見の生成に失敗しました: {e}", file=sys.stderr)
        return None
    if response.stop_reason == "refusal":
        return None
    return "".join(b.text for b in response.content if b.type == "text").strip() or None


# ── HTML ─────────────────────────────────────────────


def pct(cur, prev):
    if not prev:
        return "—"
    d = (cur - prev) / prev * 100
    return f"{'+' if d >= 0 else ''}{d:.0f}%"


def table(rows: list[dict], cols: list[tuple[str, str]], fmt=None) -> str:
    if not rows:
        return "<p style='color:#888'>データなし</p>"
    fmt = fmt or {}
    th = "".join(f"<th style='text-align:left;border-bottom:2px solid #c9a84c;padding:4px 8px'>{html.escape(h)}</th>" for _, h in cols)
    trs = []
    for r in rows:
        tds = []
        for k, _ in cols:
            v = r.get(k, "")
            v = fmt[k](v) if k in fmt else (f"{v:,.0f}" if isinstance(v, float) else v)
            tds.append(f"<td style='padding:4px 8px;border-bottom:1px solid #eee'>{html.escape(str(v))}</td>")
        trs.append("<tr>" + "".join(tds) + "</tr>")
    return f"<table style='border-collapse:collapse;font-size:13px;margin:8px 0 20px'><tr>{th}</tr>{''.join(trs)}</table>"


def md_to_html(text: str) -> str:
    import markdown

    return markdown.markdown(text, extensions=["tables"])


def build_html(ym: str, ga: dict, gsc: dict | None, posts: list[dict], commentary: str | None) -> str:
    t, tp = ga["totals"], ga["totals_prev"]
    kpi = [
        ("セッション", t.get("sessions", 0), tp.get("sessions", 0)),
        ("ユーザー", t.get("totalUsers", 0), tp.get("totalUsers", 0)),
        ("ページビュー", t.get("screenPageViews", 0), tp.get("screenPageViews", 0)),
        ("問い合わせ（フォーム送信）", ga["leads"], ga["leads_prev"]),
    ]
    if gsc:
        kpi += [
            ("検索クリック", gsc["totals"].get("clicks", 0), gsc["totals_prev"].get("clicks", 0)),
            ("検索表示回数", gsc["totals"].get("impressions", 0), gsc["totals_prev"].get("impressions", 0)),
        ]
    kpi_html = "".join(
        f"<tr><td style='padding:4px 12px 4px 0'>{n}</td><td style='padding:4px 12px;font-weight:700;text-align:right'>{c:,.0f}</td>"
        f"<td style='padding:4px 0;color:#666'>前月 {p:,.0f}（{pct(c, p)}）</td></tr>"
        for n, c, p in kpi
    )
    ai = ga["ai_sources"]
    ai_html = "、".join(f"{k} {v:,.0f}" for k, v in sorted(ai.items(), key=lambda x: -x[1])) or "なし"
    lead_html = ""
    for param, label in [("landing_page", "最初に見たページ"), ("last_article", "読んだ記事"), ("lead_referrer", "流入元"), ("form_page", "送信したページ")]:
        v = ga["lead_paths"].get(param)
        if isinstance(v, str):
            lead_html += f"<p style='color:#888;font-size:12px'>{label}: {html.escape(v)}</p>"
        else:
            lead_html += f"<h4 style='margin:12px 0 0'>{label}</h4>" + table(v, [(f"customEvent:{param}", label), ("eventCount", "件数")])
    new_posts = [p for p in posts if p["this_month"]]
    posts_html = "".join(f"<li>{p['date']} {html.escape(p['title'])}</li>" for p in new_posts) or "<li>なし</li>"
    pct_fmt = lambda v: f"{v * 100:.1f}%"
    pos_fmt = lambda v: f"{v:.1f}"

    sections = [
        f"<h1 style='font-size:20px;color:#1a1a2e'>katohpm.com 月次レポート {ym}</h1>",
        f"<div style='background:#faf8f3;border-left:3px solid #c9a84c;padding:12px 16px'>{md_to_html(commentary)}</div>" if commentary else "<p style='color:#888'>（所見は生成されませんでした）</p>",
        "<h2 style='font-size:16px;margin-top:28px'>主要な数字</h2>",
        f"<table style='font-size:14px'>{kpi_html}</table>",
        f"<p>AI アシスタントからの流入（セッション）: {ai_html}</p>",
        f"<p>英語ページの閲覧割合（上位ページ内）: {ga['en_share_top_pages'] * 100:.0f}%</p>",
        "<h2 style='font-size:16px'>今月公開した記事</h2>",
        f"<ul>{posts_html}</ul>",
        "<h2 style='font-size:16px'>問い合わせの経路</h2>",
        lead_html,
        "<h2 style='font-size:16px'>チャネル別</h2>",
        table(ga["channels"], [("sessionDefaultChannelGroup", "チャネル"), ("sessions", "セッション"), ("engagedSessions", "エンゲージ")]),
        "<h2 style='font-size:16px'>流入元</h2>",
        table(ga["sources"][:15], [("sessionSource", "参照元"), ("sessionMedium", "メディア"), ("sessions", "セッション")]),
        "<h2 style='font-size:16px'>よく見られたページ</h2>",
        table(ga["pages"][:20], [("pagePath", "パス"), ("pageTitle", "タイトル"), ("screenPageViews", "PV")]),
        "<h2 style='font-size:16px'>入口になったページ</h2>",
        table(ga["landing_pages"], [("landingPage", "ページ"), ("sessions", "セッション"), ("engagementRate", "エンゲージ率")], {"engagementRate": pct_fmt}),
    ]
    if gsc:
        sections += [
            "<h2 style='font-size:16px'>検索キーワード（Search Console）</h2>",
            table(gsc["queries"][:25], [("query", "キーワード"), ("clicks", "クリック"), ("impressions", "表示"), ("ctr", "CTR"), ("position", "平均順位")], {"ctr": pct_fmt, "position": pos_fmt}),
            "<h2 style='font-size:16px'>検索で表示されたページ</h2>",
            table(gsc["pages"], [("page", "ページ"), ("clicks", "クリック"), ("impressions", "表示"), ("position", "平均順位")], {"position": pos_fmt}),
        ]
    sections += [
        "<h2 style='font-size:16px'>国・端末</h2>",
        table(ga["countries"], [("country", "国"), ("sessions", "セッション")]),
        table(ga["devices"], [("deviceCategory", "端末"), ("sessions", "セッション")]),
        "<p style='color:#888;font-size:12px'>出典: Google Analytics 4 / Google Search Console。Search Console は数日遅れで確定するため、月初の数字は後から少し変わることがあります。</p>",
    ]
    body = "\n".join(sections)
    return f"<!doctype html><html><body style='font-family:sans-serif;color:#2a2a2a;line-height:1.7;max-width:760px'>{body}</body></html>"


# ── 送信 ─────────────────────────────────────────────


def send_email(subject: str, html_body: str):
    res = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY'].strip()}"},
        json={
            "from": "加藤プロパティマネジメント レポート <info@katohpm.com>",
            "to": [os.environ.get("REPORT_TO", "info@katohpm.com")],
            "subject": subject,
            "html": html_body,
        },
        timeout=30,
    )
    res.raise_for_status()


def load_service_account() -> dict:
    """GitHub Secrets に貼った JSON キーを読む。前後の空白・BOM・引用符は取り除く。中身はログに出さない"""
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT", "").strip().lstrip("﻿").strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "'\"":
        raw = raw[1:-1].strip()
    try:
        info = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(
            f"GOOGLE_SERVICE_ACCOUNT を JSON として読めません（長さ {len(raw)} 文字、先頭が '{{' {'である' if raw.startswith('{') else 'ではない'}）。"
            "JSON キーのファイルをメモ帳で開き、{ から } までの全文を貼り直してください。"
        )
    if info.get("type") != "service_account":
        sys.exit("GOOGLE_SERVICE_ACCOUNT がサービスアカウントの JSON キーではありません（type が service_account ではない）。")
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="対象月 YYYY-MM（既定は前月）")
    ap.add_argument("--dry-run", action="store_true", help="送信せず report.html を書き出す")
    args = ap.parse_args()

    ym = args.month or previous_month(dt.date.today())
    start, end = month_range(ym)
    prev_start, prev_end = month_range(previous_month(start))

    creds = service_account.Credentials.from_service_account_info(load_service_account(), scopes=SCOPES)
    ga = collect_ga4(GA4(creds, os.environ["GA4_PROPERTY_ID"]), start, end, prev_start, prev_end)
    try:
        gsc = collect_gsc(creds, os.environ.get("GSC_SITE_URL", "sc-domain:katohpm.com"), start, end, prev_start, prev_end)
    except Exception as e:
        print(f"Search Console の取得に失敗しました: {e}", file=sys.stderr)
        gsc = None
    posts = published_posts(start, end)

    commentary = write_commentary({"month": ym, "ga4": ga, "search_console": gsc, "posts": posts})
    report = build_html(ym, ga, gsc, posts, commentary)

    if args.dry_run or not os.environ.get("RESEND_API_KEY"):
        out = ROOT / "report.html"
        out.write_text(report, encoding="utf-8")
        print(f"wrote {out}")
        return
    send_email(f"【月次レポート】katohpm.com {ym}", report)
    print(f"sent report for {ym}")


if __name__ == "__main__":
    main()
