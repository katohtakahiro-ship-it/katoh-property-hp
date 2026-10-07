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
    '武蔵小杉を中心に川崎市・横浜市、一都3県（東京・神奈川・千葉・埼玉）に対応する宅地建物取引業者。仲介手数料は売買・賃貸とも半額。売買は法定上限（成約価格の3%＋6万円）の半額、賃貸は家賃の半額（0.5ヶ月分＋税）。来店不要。ご相談と契約手続きはフォーム・LINE・オンラインで進め、内見は現地でご案内。',
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
    /** 半額の適用条件（短文）。「半額」の表示のすぐ近くに置く（景表法の打消し表示の考え方。要確認） */
    condition: '※当社サイト・LINE・ご紹介から新規にご相談いただいた場合の料金です。当社が売主様・貸主様からお預かりして広告掲載している物件のご購入・ご入居は、各広告に表示する条件となります。',
    /** 半額の適用条件（詳細） */
    conditionDetail: [
      '対象：当社サイトのフォーム・LINE、または当社のお客様・知人からのご紹介を通じて新規にご相談いただいた、お部屋探し（借主側の仲介）、住まいの購入、住まいの売却のご依頼',
      '対象外：当社が売主様・貸主様からお預かりし、ポータルサイト等に広告掲載している物件へのお問い合わせ（当社サイト経由の場合を含む）。この場合の仲介手数料は、各広告および媒介契約書に表示する額（法定上限の範囲内）となります',
      '適用の有無は最初のお問い合わせの時点で決まり、媒介契約書（賃貸は重要事項説明）に適用する報酬額を明記します',
    ],
  },
  /** 電話番号はサイトに掲載しない（CLAUDE.md 作業ルール）。以下は未設定なら非表示 */
  /** LINE 公式アカウントの URL */
  lineUrl: '' as string,
  /** Google Analytics 4 の測定 ID。本番ビルドのときだけタグを出力する（Base.astro） */
  gaMeasurementId: 'G-P4BQ3L3J87',
  /** 代表社員（宅建業免許上の代表者は加藤良枝）。会社概要に併記する */
  representatives: ['加藤良枝', '加藤隆寛'],
  /** 紹介欄に顔出しで載せる代表（代表の一人） */
  representative: {
    name: '加藤隆寛',
    title: '代表社員',
    qualification: '宅地建物取引士',
    bio: '宅地建物取引士。横浜市生まれ、母の実家がある川崎市と横浜で育ち、いまも川崎市に住んでいます。両親が横浜・川崎で40年以上不動産業を営んできた家族とともに、東京・神奈川を中心にお部屋探し・購入・売却のご相談に対応します。旅行系 YouTube チャンネル「加藤トラベル」（登録者数35万人）も運営しています。',
    /** 詳しいプロフィールページ（ブログ記事の著者欄からもリンクする） */
    profilePath: '/company/takahiro-katoh/',
    /** graduated: false は在籍のみ（JSON-LD の alumniOf には入れない。卒業したように読める書き方をしない） */
    education: [
      { school: 'ニューヨーク市立大学シティカレッジ（The City College of New York）', detail: '在籍後、帰国して早稲田大学に入学', graduated: false },
      { school: '早稲田大学', detail: '文化構想学部 文芸・ジャーナリズム論系 卒業', graduated: true },
      { school: '一橋大学大学院', detail: '経営管理研究科（MBA）修了', graduated: true },
    ],
    /** 川崎市内で開いている合気道の道場（日英で別サイト） */
    dojo: { name: '合気道加藤道場', url: 'https://katohdojo.com/' },
    /** public/ 配下のパス。ファイルが無い間は表示しない */
    photo: '/images/representative.jpg',
    photoAlt: '代表社員 加藤隆寛',
    youtube: {
      name: '加藤トラベル',
      url: 'https://www.youtube.com/@katohtravel',
      subscribers: '35万人',
    },
  },
  /** ロゴ表記（金色の部分 + 残り） */
  logo: { accent: '加藤', rest: 'プロパティマネジメント' },
  /** トップページの <title> */
  defaultTitle: '合同会社加藤プロパティマネジメント | 仲介手数料 賃貸・売買とも半額｜武蔵小杉・川崎・横浜',
  /** JSON-LD knowsAbout */
  knowsAbout: ['武蔵小杉', '川崎市', '横浜市', '仲介手数料', '不動産売買', '賃貸仲介'],
};

export type SiteConfig = typeof SITE;

/**
 * 英語版。会社情報・料金の数値は日本語版と同一（CLAUDE.md）。表記のみ英訳。
 * 合同会社は LLC と表記する。
 */
export const SITE_EN: SiteConfig = {
  ...SITE,
  name: 'Katoh Property Management LLC',
  shortName: 'Katoh Property Management',
  description:
    'Licensed real estate brokerage based in Musashikosugi, Kawasaki, serving Kawasaki, Yokohama and the greater Tokyo area (Tokyo, Kanagawa, Chiba and Saitama). Brokerage fees are half the standard rate for both rentals and sales. No office visit needed: consultations and contract paperwork are handled via form, LINE and online meetings, and viewings take place on site. English or Japanese.',
  license: 'Licensed real estate broker: Kanagawa Prefecture Governor (2) No. 30531',
  licenseNumber: 'Kanagawa Prefecture Governor (2) No. 30531',
  address: {
    postalCode: '211-0025',
    region: 'Kanagawa',
    locality: 'Nakahara-ku, Kawasaki',
    street: '4-51-1 Kizuki',
    full: '4-51-1 Kizuki, Nakahara-ku, Kawasaki, Kanagawa 211-0025, Japan',
  },
  areaServed: ['Tokyo', 'Kanagawa', 'Chiba', 'Saitama'],
  primaryArea: 'Musashikosugi, Kawasaki and Yokohama',
  fees: {
    sale: 'half the legal maximum (1.5% of the sale price + ¥30,000, plus tax)',
    saleNote: 'the legal maximum is 3% of the sale price + ¥60,000, plus tax',
    rent: 'half a month’s rent (0.5 months + tax)',
    condition: 'These rates apply to new inquiries received through this website, LINE or a personal referral. For properties we list ourselves on behalf of a seller or landlord (including on portal sites), the fee stated in that listing applies.',
    conditionDetail: [
      'Eligible: new rental searches, home purchases and home sales requested through the form on this site, LINE, or a referral from one of our clients or acquaintances',
      'Not eligible: inquiries about properties we list on behalf of a seller or landlord on portal sites or elsewhere, even if you contact us through this site. For those, the fee stated in the listing and in the brokerage agreement applies (within the legal maximum)',
      'Eligibility is fixed at the time of your first inquiry, and the applicable fee is written into the brokerage agreement (for rentals, the explanation of important matters)',
    ],
  },
  representatives: ['Yoshie Katoh', 'Takahiro Katoh'],
  representative: {
    ...SITE.representative,
    name: 'Takahiro Katoh',
    title: 'Managing Member',
    qualification: 'Licensed Real Estate Transaction Specialist (Takken-shi)',
    bio: 'Licensed real estate transaction specialist (takken-shi). Born in Yokohama and raised between Yokohama and Kawasaki, where the family on the mother’s side is from, and still living in Kawasaki. Together with parents who have run a real estate business in Yokohama and Kawasaki for over 40 years, handles rentals, purchases and sales across Tokyo and Kanagawa, in English or Japanese. Also runs the travel YouTube channel "Katoh Travel" (350,000 subscribers).',
    profilePath: '/en/company/takahiro-katoh/',
    education: [
      { school: 'The City College of New York (CUNY)', detail: 'attended before returning to Japan to study at Waseda University', graduated: false },
      { school: 'Waseda University', detail: 'BA, School of Culture, Media and Society (Contemporary Literature and Criticism)', graduated: true },
      { school: 'Hitotsubashi University', detail: 'MBA, Graduate School of Business Administration', graduated: true },
    ],
    dojo: { name: 'Aikido Katoh Dojo', url: 'https://katohdojo-en.com/' },
    photoAlt: 'Takahiro Katoh, Managing Member',
    youtube: { ...SITE.representative.youtube, name: 'Katoh Travel', subscribers: '350,000' },
  },
  logo: { accent: 'Katoh', rest: ' Property Management' },
  defaultTitle: 'Katoh Property Management LLC | Half-price brokerage fees in Musashikosugi, Kawasaki & Yokohama',
  knowsAbout: ['Musashikosugi', 'Kawasaki', 'Yokohama', 'brokerage fees', 'buying property in Japan', 'renting in Japan'],
};

export const siteFor = (locale: 'ja' | 'en'): SiteConfig => (locale === 'en' ? SITE_EN : SITE);
