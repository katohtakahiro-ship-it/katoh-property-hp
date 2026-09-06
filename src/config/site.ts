/**
 * サイト全体で共有する会社情報・料金。
 * 値は CLAUDE.md「会社情報（正式・変更不可）」「料金体系」に従う。推測で変更しないこと。
 */
export const SITE = {
  name: '合同会社加藤プロパティマネジメント',
  shortName: '加藤プロパティマネジメント',
  /** TODO: 独自ドメイン取得後に変更（Cloudflare Pages の既定ドメインを仮置き） */
  url: 'https://katoh-property-hp.pages.dev',
  description:
    '武蔵小杉を中心に川崎市・横浜市、一都3県（東京・神奈川・千葉・埼玉）に対応する宅地建物取引業者。仲介手数料は売買・賃貸とも半額。売買は法定上限（成約価格の3%＋6万円）の半額、賃貸は家賃の半額（0.5ヶ月分＋税）。来店不要、電話・フォーム・LINEでオンライン完結。',
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
  /** 電話番号・受付時間は未確定のため空。設定すると Contact セクションに表示される */
  tel: '' as string,
  hours: '' as string,
  /** LINE 公式アカウントの URL。未設定なら非表示 */
  lineUrl: '' as string,
} as const;

export const NAV_LINKS = [
  { href: '/#fee', label: '仲介手数料' },
  { href: '/#areas', label: '対応エリア' },
  { href: '/#flow', label: 'ご利用の流れ' },
  { href: '/#faq', label: 'よくある質問' },
] as const;
