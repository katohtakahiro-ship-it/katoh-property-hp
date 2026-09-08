# 合同会社加藤プロパティマネジメント 公式サイト

Astro で作った静的サイトです。会社情報・料金・作業ルールは [CLAUDE.md](CLAUDE.md) を正とします。

- 本番: https://katohpm.com （日本語）、https://katohpm.com/en/ （英語）
- リポジトリ: https://github.com/katohtakahiro-ship-it/katoh-property-hp
- ホスティング: Cloudflare Pages（GitHub の main に push すると自動デプロイ）

## 構成

```
src/
  config/site.ts        会社情報・料金（日本語 SITE と英語 SITE_EN）。ここを直せば全ページに反映
  i18n.ts               ナビ・ブログなどの UI 文言（日英）
  content.config.ts     ブログ記事の frontmatter 定義
  content/blog/ja/      日本語記事（Markdown）
  content/blog/en/      英語記事（同じファイル名で対にする。当面は未使用）
  layouts/Base.astro    共通レイアウト（ヘッダー・フッター・JSON-LD・hreflang）
  layouts/Post.astro    記事レイアウト（FAQ ブロックと FAQPage JSON-LD を自動生成）
  pages/index.astro     日本語トップ    pages/en/index.astro  英語トップ
  pages/blog/           日本語ブログ    pages/en/blog/        英語ブログ
  styles/               global.css（全体）、home.css（トップページ）
public/
  admin/                Sveltia CMS（config.yml と index.html）
  images/               画像。代表写真は public/images/representative.jpg
design/index.html       参考デザイン（トップページの見た目の基準）
```

## ローカルで確認

Node.js 22 以上が必要です（インストール済みなら次の手順だけで動きます）。

```bash
npm install
```

```bash
npm run dev
```

ブラウザで http://localhost:4321 を開きます。ファイルを保存すると自動で再読み込みされます。

そのほかのコマンド:

| コマンド | 内容 |
| --- | --- |
| `npm run build` | 本番用にビルド（`dist/` に出力）。Cloudflare Pages はこれを実行する |
| `npm run preview` | ビルド結果をローカルで確認 |
| `npm run check` | 型チェック（`astro check`） |

`draft: true` の記事は dev でもビルドでも表示されません。確認したいときは一時的に `false` にしてください。

## Cloudflare Pages に接続

初回だけ、Cloudflare の管理画面で GitHub と接続します。以後は main に push するだけで自動デプロイされます。

1. https://dash.cloudflare.com → 左メニュー「コンピュート（Workers & Pages）」→「作成」→「Pages」タブ →「Git に接続」
2. GitHub アカウントを連携し、リポジトリ `katohtakahiro-ship-it/katoh-property-hp` を選択
3. ビルド設定
   - フレームワークプリセット: **Astro**
   - ビルドコマンド: `npm run build`
   - ビルド出力ディレクトリ: `dist`
   - 環境変数: `NODE_VERSION` = `22`
4. 「保存してデプロイ」。数分で `https://katoh-property-hp.pages.dev` に公開される
5. カスタムドメインの設定: プロジェクト →「カスタムドメイン」→「ドメインを設定」で `katohpm.com` を追加。同じ Cloudflare アカウントでドメインを管理しているので DNS レコードは自動で作られる。続けて `www.katohpm.com` も追加（自動で katohpm.com へリダイレクトされる）
6. 反映後、https://katohpm.com が表示されることと、DNS の「推奨事項」の警告が消えたことを確認

補足:

- プレビュー: main 以外のブランチや Pull Request を作ると、自動でプレビュー URL が発行されます
- 問い合わせフォームの送信処理（`/api/contact`、Cloudflare Pages Functions + Resend）は未実装です。実装時は Pages の環境変数に Resend の API キーを設定します
- Cloudflare は新規プロジェクトに Workers を推奨していますが、この構成では Pages で問題ありません。必要になれば Astro の Cloudflare アダプタで移行できます

## 記事を追加

### 方法 1: ファイルを書く（Claude Code / エディタ）

1. `src/content/blog/ja/<slug>.md` を作る。`<slug>` は半角英数とハイフン（例: `musashikosugi-chukai-tesuryo`）。URL は `/blog/<slug>/` になる
2. frontmatter は次の形。`page_slug` はファイル名と同じにする

```markdown
---
page_slug: example-slug
title: 質問文のタイトルにする
date: 2026-09-09
description: 検索結果と一覧に出る説明。結論を含める
tags: [武蔵小杉, 仲介手数料]
draft: true
faq:
  - q: 質問
    a: 回答（結論を先に）
---

## 最初の見出しも質問文にする

**結論：1〜2文で書く。** 続けて説明。
```

3. 書き方のルール（CLAUDE.md より）: H2 は必ず質問文にし、直後に結論を1〜2文で書く。会社情報・料金は CLAUDE.md の値を使う。「無料」は使わない。法令に関する記述は断定せず「要確認」と書く。データは公的データを出典付きで使う
4. 記事末尾の FAQ ブロックと FAQPage の JSON-LD は、frontmatter の `faq` から自動生成される
5. 公開するときは `draft: false` にして commit、main に push。数分で本番に反映される
6. 英語版を出す場合は `src/content/blog/en/` に**同じファイル名**で置く。日英の記事ページが自動で相互リンクされ、hreflang が付く

### 方法 2: ブラウザから書く（Sveltia CMS）

https://katohpm.com/admin/ を開き、GitHub でログインして編集します。保存すると main に直接コミットされ、自動デプロイされます。初回だけ下の「GitHub OAuth の設定」が必要です。

- 「下書き」をオフにすると公開されます
- 画像は `public/images/blog/` に保存され、本文からは `/images/blog/ファイル名` で参照されます
- 英語版は、記事の編集画面で言語を「en」に切り替えて書きます（同じファイル名で保存されます）

## Sveltia CMS の GitHub OAuth 設定（初回のみ）

Sveltia CMS は GitHub にログインするために、OAuth の仲介サーバーが必要です。Sveltia 公式の Cloudflare Worker「Sveltia CMS Authenticator」を使います（無料枠で十分）。

1. **Worker をデプロイ**
   https://github.com/sveltia/sveltia-cms-auth を開き、README の「Deploy to Cloudflare Workers」ボタンから、Cloudflare アカウントにデプロイします。完了すると `https://sveltia-cms-auth.<アカウント名>.workers.dev` のような URL ができます（この URL を控える）
2. **GitHub に OAuth App を作成**
   GitHub → 右上のアイコン → Settings → Developer settings → OAuth Apps →「New OAuth App」
   - Application name: `Katoh PM CMS`
   - Homepage URL: `https://katohpm.com`
   - Authorization callback URL: `https://sveltia-cms-auth.<アカウント名>.workers.dev/callback`（手順1の URL + `/callback`）
   - 作成後に表示される **Client ID** を控え、「Generate a new client secret」で **Client secret** を発行して控える（secret は一度しか表示されません）
3. **Worker に環境変数を設定**
   Cloudflare → Workers & Pages → `sveltia-cms-auth` → 設定 → 変数
   - `GITHUB_CLIENT_ID`: 手順2の Client ID
   - `GITHUB_CLIENT_SECRET`: 手順2の Client secret（「暗号化」にする）
   - `ALLOWED_DOMAINS`: `katohpm.com`（複数ある場合はカンマ区切り。`*.pages.dev` を足すとプレビュー URL からもログインできます）
   保存後に Worker を再デプロイ
4. **config.yml の URL を差し替え**
   [public/admin/config.yml](public/admin/config.yml) の `base_url` を手順1の Worker の URL に書き換えて commit、push
5. **動作確認**
   https://katohpm.com/admin/ を開き、「Sign in with GitHub」→ GitHub の認可画面で Authorize。記事一覧が表示されれば完了

補足:

- ログインできるのは、リポジトリに書き込み権限がある GitHub アカウントだけです
- Client secret は漏れると他人がログインできる可能性があるので、Worker の変数以外には保存しないでください
- ローカルでは http://localhost:4321/admin/index.html を開くと（dev サーバーは `/admin/` だけでは 404 になります）、OAuth なしで「ローカルリポジトリで作業」からファイルを直接編集できます（Chrome / Edge）

## 会社情報・料金を変える

[src/config/site.ts](src/config/site.ts) の `SITE`（日本語）と `SITE_EN`（英語）を直します。トップページ、フッター、JSON-LD、記事末尾の CTA にまとめて反映されます。変更したら [CLAUDE.md](CLAUDE.md) の値も揃えてください。

## 未着手の項目

- 問い合わせフォームの送信処理（Cloudflare Pages Functions + Resend）
- LINE 公式アカウントの URL（`src/config/site.ts` の `lineUrl`。設定すると LINE ボタンが表示される）
- 代表写真 `public/images/representative.jpg`（置くだけで表示される）
- 目的別ページ（/buy/ /sell/ /rent/）、エリアページ、会社概要ページ
- Google Analytics 4 / Search Console の設定
- タワーマンション成約価格ウォッチ用のスクリプト（`/scripts/`、`/data/`）
