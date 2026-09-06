# 合同会社加藤プロパティマネジメント 公式サイト

## 会社情報（正式・変更不可）
- 社名：合同会社加藤プロパティマネジメント
- 免許：宅地建物取引業 神奈川県知事（2）第30531号
- 住所：〒211-0025 神奈川県川崎市中原区木月4-51-1
- 対応エリア：一都3県（東京・神奈川・千葉・埼玉）
- 主戦場：武蔵小杉を中心に川崎市・横浜市
- 事務所は自宅兼用。来店は想定せず、電話・フォーム・LINEでオンライン完結型の対応

## 料金体系（サイト全体で必ず統一）
- 売買仲介：成約価格の 1%（税別）※法定上限は3%+6万円
- 賃貸仲介：家賃の半額（0.5ヶ月分＋税）
- 「無料」という表現は使わない

## サイトの目的
1. 宅建業者としてのコーポレートサイト（会社概要・料金・免許・問い合わせ）
2. ブログを書き溜めるメディアサイト（東京R不動産／渋井不動産型）
3. GEO対策：ChatGPT/Claude/Gemini/Perplexity が「武蔵小杉 不動産」「川崎 仲介手数料 安い」等の質問で当社を引用・推薦するよう、Q&A形式の構造化コンテンツを重視

## 技術スタック
- 静的サイト：Astro（Content Collections で記事管理）
- ホスティング：Cloudflare Pages（GitHub連携で自動デプロイ、無料）
- 記事編集：Claude Code が主。ウェブ編集用に Sveltia CMS を /admin/ に設置（GitHub OAuth）
- 問い合わせ：Cloudflare Pages Functions + Resend（またはFormspree）でメール送信
- 分析：Google Analytics 4 / Search Console
- ドメイン：未定（Cloudflare Registrar で取得予定）
- Googleビジネスプロフィールは使わない（自宅事務所のため）
- WordPress / AFFINGER は使わない

## ディレクトリ構成（予定）
- /design/ … 参考デザイン（index.html）。トップページの見た目の基準
- /src/ … Astro ソース（pages, layouts, components, content）
- /src/content/blog/ … 記事（Markdown、frontmatter に title/date/description/tags/faq）
- /public/admin/ … Sveltia CMS
- /scripts/ … 国交省 不動産情報ライブラリAPI（XIT001）で川崎・横浜のタワマン成約価格を四半期ごとに取得・集計・グラフ化するPython
- /data/ … API取得データ（CSV）。生成したグラフは /public/charts/ に出力

## デザイン方針
- /design/index.html のトーンを踏襲：紺（#1a1a2e）×ゴールド（#c9a84c）×生成り（#faf8f3）、明朝体
- 高級感より「誠実・明快」。数字（1%・半額）が主役
- モバイル優先

## コンテンツ方針
- 記事は必ず H2 に質問文を置き、直後に結論を1〜2文で書く（AI引用されやすくする）
- 記事末尾にFAQ（Q/A）ブロックを置き、frontmatter の faq からJSON-LD（FAQPage schema）を自動生成する
- 全ページに Organization / RealEstateAgent の JSON-LD を出力（免許番号・住所を含む）
- 定期連載：川崎・横浜タワマン成約価格ウォッチ（四半期）／武蔵小杉・元住吉・新丸子エリア比較
- データは国交省の成約価格（公的データ）を出典明記で使う。SUUMO等のスクレイピングはしない

## 作業ルール
- 会社情報・料金は必ず本ファイルの値を使う。推測で書かない
- 法令関連（宅建業法の表示義務、景表法）は断定せず、要確認として明記する
- 日本語で応答する
