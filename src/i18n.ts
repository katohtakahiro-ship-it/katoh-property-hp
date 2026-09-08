/**
 * 多言語対応の共通定義。
 * - 日本語（ja）が既定で URL 接頭辞なし、英語（en）は /en/ 配下
 * - UI 文言（ナビ・ブログ・CTA など）はここで管理する。会社情報・料金は src/config/site.ts
 */
export const LOCALES = ['ja', 'en'] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = 'ja';

export const otherLocale = (locale: Locale): Locale => (locale === 'ja' ? 'en' : 'ja');

/** ロケールに応じたパスを返す。localePath('en', '/blog/') → '/en/blog/' */
export const localePath = (locale: Locale, path: string): string => {
  if (locale === DEFAULT_LOCALE) return path;
  return `/en${path.startsWith('/') ? path : `/${path}`}`;
};

export const HTML_LANG: Record<Locale, string> = { ja: 'ja', en: 'en' };
export const OG_LOCALE: Record<Locale, string> = { ja: 'ja_JP', en: 'en_US' };
export const DATE_LOCALE: Record<Locale, string> = { ja: 'ja-JP', en: 'en-US' };

export const formatDate = (d: Date, locale: Locale) =>
  d.toLocaleDateString(DATE_LOCALE[locale], {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'Asia/Tokyo',
  });

/** ナビ項目（ラベルは UI[locale].nav から） */
export const NAV_ITEMS = [
  { key: 'blog', path: '/blog/' },
  { key: 'fee', path: '/#fee' },
  { key: 'company', path: '/#company' },
] as const;

export const UI = {
  ja: {
    switchLabel: 'English',
    switchAria: 'Switch to English',
    menuOpen: 'メニューを開く',
    menuClose: 'メニューを閉じる',
    navAria: 'メインナビゲーション',
    nav: { blog: 'ブログ', fee: '仲介手数料', company: '会社情報', contact: 'お問い合わせ' },
    blog: {
      title: 'ブログ',
      heading: '記事一覧',
      description:
        '武蔵小杉・川崎・横浜の不動産、仲介手数料、タワーマンションの成約価格などについて、加藤プロパティマネジメントがQ&A形式で解説する記事一覧です。',
      empty: '記事は準備中です。',
      back: '← 記事一覧へ',
      updated: '更新',
      faqHeading: 'この記事のよくある質問',
      ctaTitle: '仲介手数料は賃貸・売買とも半額',
      ctaBody: '武蔵小杉を中心に川崎市・横浜市、一都3県に対応。来店不要、フォーム・LINEでオンライン完結です。',
      ctaButton: '相談する',
      readInOther: 'Read this article in English',
    },
  },
  en: {
    switchLabel: '日本語',
    switchAria: '日本語ページへ切り替える',
    menuOpen: 'Open menu',
    menuClose: 'Close menu',
    navAria: 'Main navigation',
    nav: { blog: 'Blog', fee: 'Fees', company: 'Company', contact: 'Contact' },
    blog: {
      title: 'Blog',
      heading: 'Articles',
      description:
        'Plain-language Q&A articles from Katoh Property Management about renting and buying around Musashikosugi, Kawasaki and Yokohama, brokerage fees, and tower-condo sale prices.',
      empty: 'Articles are coming soon.',
      back: '← All articles',
      updated: 'Updated',
      faqHeading: 'Frequently asked questions about this article',
      ctaTitle: 'Half-price brokerage fees for rentals and sales',
      ctaBody:
        'Serving Musashikosugi, Kawasaki, Yokohama and the greater Tokyo area. No office visit needed: everything is handled online via form or LINE, in English or Japanese.',
      ctaButton: 'Contact us',
      readInOther: 'この記事を日本語で読む',
    },
  },
} as const satisfies Record<Locale, unknown>;

export type UIStrings = (typeof UI)[Locale];
