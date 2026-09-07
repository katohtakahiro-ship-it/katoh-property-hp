/**
 * サイト全体で共有する会社情報・料金。
 * 値は CLAUDE.md「会社情報（正式・変更不可）」「料金体系」に従う。推測で変更しないこと。
 */
export const SITE = {
  name: '合同会社加藤プロパティマネジメント',
  shortName: '加藤プロパティマネジメント',
  /** 独自ドメイン（astro.config.mjs の site と揃える） */
  url: 'https://katohpm.com',
  description:
    '武蔵小杉を中心に川崎市・横浜市、一都3県（東京・神奈川・千葉・埼玉）に対応する宅地建物取引業者。仲介手数料は売買・賃貸とも半額。売買は法定上限（成約価格の3%＋6万円）の半額、賃貸は家賃の半額（0.5ヶ月分＋税）。来店不要、フォーム・LINEでオンライン完結。',
  license: '宅地建物取引業 神奈川県知事（2）第30531号',
  licenseNumber: '神奈川県知事（2）第30531号',
  address: {
    postalCode: '211-0025',
    region: '神奈川県',
    locality: '川崎市中原区',
    street: '木月4-51-1',
    full: '〒211-0025 神奈川県川崎市中原区木月4-51-1',
  },
  areaServed: ['東京都', '神奈川県', '千葉県', '埼玉県'],
  primaryArea: '武蔵小杉を中心に川崎市・横浜市',
  fees: {
    sale: '法定上限の半額（成約価格の1.5%＋3万円、税別）',
    saleNote: '法定上限は成約価格の3%＋6万円（税別）',
    rent: '家賃の半額（0.5ヶ月分＋税）',
  },
  /** 電話番号はサイトに掲載しない（CLAUDE.md 作業ルール）。以下は未設定なら非表示 */
  /** LINE 公式アカウントの URL */
  lineUrl: '' as string,
  /** 代表社員（宅建業免許上の代表者は加藤良枝）。会社概要に併記する */
  representatives: ['加藤良枝', '加藤隆寛'],
  /** 紹介欄に顔出しで載せる代表（代表の一人） */
  representative: {
    name: '加藤隆寛',
    title: '代表社員',
    bio: '旅行系 YouTube チャンネル「加藤トラベル」（登録者数35万人）を運営。川崎市在住。武蔵小杉を中心に、地元の目線で物件探し・売却のご相談に対応します。',
    /** public/ 配下のパス。ファイルが無い間は表示しない */
    photo: '/images/representative.jpg',
    photoAlt: '代表社員 加藤隆寛',
    youtube: {
      name: '加藤トラベル',
      url: 'https://www.youtube.com/@katohtravel',
      subscribers: '35万人',
    },
  },
} as const;

/** ナビは最小限（CLAUDE.md サイト構成方針）。会社情報は /company/ 作成後に差し替える */
export const NAV_LINKS = [
  { href: '/blog/', label: 'ブログ' },
  { href: '/#fee', label: '仲介手数料' },
  { href: '/#company', label: '会社情報' },
] as const;
