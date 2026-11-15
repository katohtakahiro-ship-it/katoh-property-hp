/**
 * 物件種別ページ（/buy/ の下。新築戸建て・中古マンション・中古戸建て）の内容。日英。
 * ルール（CLAUDE.md）: 見出しは質問文、直後に結論。料金・会社情報は site.ts の値を使う。「無料」は使わない。法令は要確認と書く。
 * 2026-11-13: 中古マンションから公開。新築戸建て・中古戸建ては順に追加する。
 */
import { siteFor } from '../config/site';
import type { Locale } from '../i18n';

export type BuyTypeKey = 'chuko-mansion';

export interface TypeSection {
  /** 質問文の見出し */
  q: string;
  /** 結論（太字で先頭に出す） */
  a: string;
  body?: string[];
  list?: string[];
  /** 表（任意）。横に長い場合はスクロール */
  table?: { caption: string; head: string[]; rows: string[][]; note?: string };
  /** 本文の下に置くリンク（任意） */
  links?: { label: string; href: string; external?: boolean }[];
}

export interface BuyTypeContent {
  key: BuyTypeKey;
  path: string;
  /** パンくず・カードで使う短い名前 */
  label: string;
  /** <title> と h1（｜の前が h1） */
  title: string;
  description: string;
  eyebrow: string;
  lead: string;
  /** Service JSON-LD の serviceType */
  serviceType: string;
  sections: TypeSection[];
  steps: { title: string; body: string }[];
  faq: { q: string; a: string }[];
  /** 関連記事のスラッグ（日英共通） */
  relatedSlugs: string[];
  /** 本文末の注記（出典など） */
  notes: string[];
  ctaTitle: string;
}

/** 日英で対になるパス */
export const BUY_TYPE_PATH: Record<BuyTypeKey, Record<Locale, string>> = {
  'chuko-mansion': { ja: '/buy/chuko-mansion/', en: '/en/buy/resale-condo/' },
};

/** 国土交通省 不動産情報ライブラリ（成約価格情報）2025年1〜12月、中古マンション等の成約㎡単価の中央値（当社集計） */
const WARD_ROWS_JA: string[][] = [
  ['川崎市（全体）', '64.7万円', '約4,530万円', '2,527件'],
  ['川崎市中原区', '104.3万円', '約7,300万円', '543件'],
  ['川崎市幸区', '78.8万円', '約5,520万円', '301件'],
  ['川崎市高津区', '62.7万円', '約4,390万円', '378件'],
  ['川崎市川崎区', '60.0万円', '約4,200万円', '395件'],
  ['川崎市宮前区', '53.5万円', '約3,750万円', '458件'],
  ['川崎市多摩区', '45.9万円', '約3,220万円', '224件'],
  ['川崎市麻生区', '39.4万円', '約2,760万円', '228件'],
  ['横浜市（全体）', '51.7万円', '約3,620万円', '5,786件'],
  ['横浜市西区', '97.1万円', '約6,800万円', '400件'],
  ['横浜市中区', '75.0万円', '約5,250万円', '471件'],
  ['横浜市神奈川区', '67.3万円', '約4,710万円', '495件'],
  ['横浜市港北区', '62.8万円', '約4,390万円', '710件'],
  ['横浜市都筑区', '61.4万円', '約4,300万円', '340件'],
  ['横浜市青葉区', '55.0万円', '約3,850万円', '435件'],
  ['横浜市鶴見区', '50.0万円', '約3,500万円', '460件'],
  ['横浜市南区', '47.3万円', '約3,310万円', '369件'],
  ['横浜市泉区', '42.7万円', '約2,990万円', '83件'],
  ['横浜市戸塚区', '42.3万円', '約2,960万円', '392件'],
  ['横浜市緑区', '41.9万円', '約2,930万円', '216件'],
  ['横浜市瀬谷区', '38.8万円', '約2,710万円', '42件'],
  ['横浜市保土ケ谷区', '35.3万円', '約2,470万円', '255件'],
  ['横浜市栄区', '35.2万円', '約2,460万円', '132件'],
  ['横浜市磯子区', '35.0万円', '約2,450万円', '283件'],
  ['横浜市港南区', '33.3万円', '約2,330万円', '243件'],
  ['横浜市金沢区', '28.1万円', '約1,970万円', '276件'],
  ['横浜市旭区', '26.0万円', '約1,820万円', '184件'],
];

const WARD_ROWS_EN: string[][] = [
  ['Kawasaki (whole city)', '¥647,000', '≈ ¥45,300,000', '2,527'],
  ['Nakahara Ward, Kawasaki', '¥1,043,000', '≈ ¥73,000,000', '543'],
  ['Saiwai Ward, Kawasaki', '¥788,000', '≈ ¥55,200,000', '301'],
  ['Takatsu Ward, Kawasaki', '¥627,000', '≈ ¥43,900,000', '378'],
  ['Kawasaki Ward, Kawasaki', '¥600,000', '≈ ¥42,000,000', '395'],
  ['Miyamae Ward, Kawasaki', '¥535,000', '≈ ¥37,500,000', '458'],
  ['Tama Ward, Kawasaki', '¥459,000', '≈ ¥32,200,000', '224'],
  ['Asao Ward, Kawasaki', '¥394,000', '≈ ¥27,600,000', '228'],
  ['Yokohama (whole city)', '¥517,000', '≈ ¥36,200,000', '5,786'],
  ['Nishi Ward, Yokohama', '¥971,000', '≈ ¥68,000,000', '400'],
  ['Naka Ward, Yokohama', '¥750,000', '≈ ¥52,500,000', '471'],
  ['Kanagawa Ward, Yokohama', '¥673,000', '≈ ¥47,100,000', '495'],
  ['Kohoku Ward, Yokohama', '¥628,000', '≈ ¥43,900,000', '710'],
  ['Tsuzuki Ward, Yokohama', '¥614,000', '≈ ¥43,000,000', '340'],
  ['Aoba Ward, Yokohama', '¥550,000', '≈ ¥38,500,000', '435'],
  ['Tsurumi Ward, Yokohama', '¥500,000', '≈ ¥35,000,000', '460'],
  ['Minami Ward, Yokohama', '¥473,000', '≈ ¥33,100,000', '369'],
  ['Izumi Ward, Yokohama', '¥427,000', '≈ ¥29,900,000', '83'],
  ['Totsuka Ward, Yokohama', '¥423,000', '≈ ¥29,600,000', '392'],
  ['Midori Ward, Yokohama', '¥419,000', '≈ ¥29,300,000', '216'],
  ['Seya Ward, Yokohama', '¥388,000', '≈ ¥27,100,000', '42'],
  ['Hodogaya Ward, Yokohama', '¥353,000', '≈ ¥24,700,000', '255'],
  ['Sakae Ward, Yokohama', '¥352,000', '≈ ¥24,600,000', '132'],
  ['Isogo Ward, Yokohama', '¥350,000', '≈ ¥24,500,000', '283'],
  ['Konan Ward, Yokohama', '¥333,000', '≈ ¥23,300,000', '243'],
  ['Kanazawa Ward, Yokohama', '¥281,000', '≈ ¥19,700,000', '276'],
  ['Asahi Ward, Yokohama', '¥260,000', '≈ ¥18,200,000', '184'],
];

const API_NOTICE_JA =
  '成約単価は、国土交通省「不動産情報ライブラリ」の成約価格情報（API）を用いて当社が集計・加工したものです。このサービスは、国土交通省の不動産情報ライブラリのAPI機能を使用していますが、提供情報の最新性、正確性、完全性等が保証されたものではありません。';
const API_NOTICE_EN =
  'Unit prices were compiled and processed by us from the transaction-price data (API) of the Real Estate Information Library of Japan’s Ministry of Land, Infrastructure, Transport and Tourism. This service uses the Library’s API, but the timeliness, accuracy and completeness of the information are not guaranteed.';

export function getBuyTypePages(locale: Locale): Record<BuyTypeKey, BuyTypeContent> {
  const S = siteFor(locale);
  const ja = locale === 'ja';

  if (ja) {
    return {
      'chuko-mansion': {
        key: 'chuko-mansion',
        path: BUY_TYPE_PATH['chuko-mansion'].ja,
        label: '中古マンション',
        title: '川崎・横浜で中古マンションを買う方へ｜仲介手数料は法定上限の半額',
        description: `川崎市・横浜市の中古マンション購入を、仲介手数料${S.fees.sale}で仲介します。価格は国土交通省の成約価格データで、管理の状態は重要事項調査報告書などの書類で確かめます。区別の成約㎡単価（2025年）も掲載。来店不要、内見は現地でご案内します。`,
        eyebrow: 'Resale Condominiums',
        lead: `価格は国の成約データで、管理の状態は書類で確かめてから判断します。川崎市・横浜市を中心に、中古マンションの購入を仲介手数料${S.fees.sale}で仲介します。`,
        serviceType: '中古マンションの購入仲介',
        sections: [
          {
            q: '中古マンションの仲介手数料はいくらですか？',
            a: `${S.fees.sale}です。7,000万円の中古マンションなら 1,188,000円（税込）で、法定上限（2,376,000円）との差は 1,188,000円になります。`,
            body: ['率は物件によらず同じです。ローン事務代行手数料などの名目の費用はいただきません。費用が発生するのは成約時のみです。'],
          },
          {
            q: '川崎市・横浜市の中古マンション相場はどのくらいですか？',
            a: '国土交通省の成約価格データを当社で集計すると、2025年の中古マンションの成約㎡単価（中央値）は川崎市全体で64.7万円、横浜市全体で51.7万円でした。区別では、武蔵小杉のある川崎市中原区（104.3万円）と、みなとみらいのある横浜市西区（97.1万円）が高くなっています。',
            table: {
              caption: '川崎市・横浜市の中古マンション成約㎡単価（2025年、区別の中央値）',
              head: ['市区', '成約㎡単価（中央値）', '70㎡に換算', '件数'],
              rows: WARD_ROWS_JA,
              note: '出典：国土交通省 不動産情報ライブラリ（成約価格情報）をもとに当社集計。2025年1〜12月、中古マンション等。築年数・広さの違いは調整していないため、区ごとの水準をつかむための目安です。',
            },
            body: ['同じ区でも、駅からの距離や築年数で価格は大きく変わります。気になる物件があれば、同じマンションと周辺の成約事例をお調べしてご説明します。'],
            links: [
              { label: '武蔵小杉の中古マンションは東京23区を超えたのか？（記事）', href: '/blog/musashikosugi-mansion-2021-2025/' },
              { label: '川崎市のマンション価格の目安をその場で調べる（簡易査定）', href: '/sell/satei/' },
            ],
          },
          {
            q: '価格が適正かどうか、どう判断しますか？',
            a: '国土交通省の成約価格データと、同じマンション・周辺の最近の成約事例を照らし合わせて判断します。売り出し価格ではなく「実際に売れた価格」と比べるのがポイントです。',
            body: ['築年数、階数、向き、リフォームの有無で価格は変わりますので、比べる事例の条件をそろえてご説明します。相場より高いと判断した場合は、価格交渉の材料としてもお使いいただけます。'],
          },
          {
            q: '管理の状態は何で確認しますか？',
            a: '管理会社が作成する「重要事項調査報告書」と、長期修繕計画・管理規約などの書類で確認します。マンションは「管理を買う」と言われるほど、管理の状態が住み心地と資産価値を左右します。',
            list: [
              '修繕積立金の積立額と残高、今後の値上げの予定',
              '管理費・修繕積立金の滞納の有無（マンション全体）',
              '大規模修繕工事の実施履歴と次回の予定',
              '管理組合の総会議事録（揉め事や大きな出費の予定がないか）',
              '管理規約・使用細則（ペット、リフォーム、民泊などの制限）',
            ],
          },
          {
            q: '修繕積立金が安いマンションは得ですか？',
            a: '必ずしも得ではありません。積立金が少ないと、将来の大幅な値上げや、大規模修繕のときの一時金の負担につながることがあります。',
            body: ['長期修繕計画の金額と現在の積立額を比べ、不足がないかを確認します。国土交通省の「マンションの修繕積立金に関するガイドライン」の目安と比べる方法もあります（目安の数値は要確認）。'],
          },
          {
            q: '築年数と耐震基準はどう見ればよいですか？',
            a: '1981年6月1日以降に建築確認を受けた「新耐震基準」の建物かどうかが一つの目安です。築年数だけでなく、建築確認の日付を確認します。',
            body: ['住宅ローン減税は、1982年以降に建築された住宅であれば新耐震基準に適合しているものとして扱われます。それより前の建物でも、耐震基準適合証明書などで対象になる場合があります（要件は要確認）。'],
          },
          {
            q: '武蔵小杉などのタワーマンションを買うときの注意点は？',
            a: '眺望や共用施設だけでなく、管理費・修繕積立金の水準と、災害への備えを確認します。',
            body: ['2019年の台風19号では、武蔵小杉の一部のタワーマンションで地下の電気設備が浸水し、停電や断水が起きました。電気設備の位置と浸水対策、非常用電源の有無を確認します。多摩川沿いの浸水想定はハザードマップで確かめられます。'],
            list: [
              '管理費・修繕積立金の水準と、超高層ならではの修繕費（外壁・エレベーターなど）の見込み',
              '電気設備の位置、浸水対策、非常用発電機と停電時のエレベーター',
              '同じ建物内の階数・向きによる価格差',
            ],
            links: [
              { label: '川崎市でタワマンが多い区は？（記事）', href: '/blog/kawasaki-tower-mansion-ku-betsu/' },
              { label: 'ハザードマップポータルサイト（国土交通省）', href: 'https://disaportal.gsi.go.jp/', external: true },
            ],
          },
          {
            q: 'リフォームを前提に買うときは何を確認しますか？',
            a: '管理規約で工事の内容に制限がないか（床材の遮音等級、水回りの移動など）を先に確認し、内見のときに工事費の見込みを立てます。',
            body: ['購入価格とリフォーム費用の合計で予算を組み、住宅ローンにリフォーム費用を含められるかも金融機関に確認します。'],
          },
          {
            q: 'SUUMO などで見つけた中古マンションも仲介してもらえますか？',
            a: 'はい。物件の URL をお送りください。売買物件の多くは不動産会社どうしの情報網（レインズ）で共有されていますので、原則として当社から購入の申込ができます。',
            body: ['売主側の会社だけで扱う物件もありますので、その場合は確認のうえお伝えします。'],
            links: [{ label: 'SUUMOで見つけた物件、別の不動産会社で買える？（記事）', href: '/blog/portal-bukken-url-chukai/' }],
          },
        ],
        steps: [
          { title: 'お問い合わせ', body: '希望エリア・予算・時期や、気になる物件の URL を、下のフォームか LINE でお送りください。' },
          { title: '相場と資金計画', body: '成約価格データで相場をご説明し、住宅ローンの事前審査のタイミングをご案内します。' },
          { title: '内見と書類の確認', body: '現地で物件をご案内し、重要事項調査報告書や長期修繕計画で管理の状態を確認します。' },
          { title: '購入申込・契約', body: '価格や条件の交渉、重要事項説明、売買契約を進めます。' },
          { title: '決済・お引渡し', body: `仲介手数料は${S.fees.sale}。ローン実行と登記手続きまでサポートします。` },
        ],
        faq: [
          { q: '中古マンションの仲介手数料はいくらですか？', a: `${S.fees.sale}です。7,000万円の物件なら1,188,000円（税込）で、法定上限との差は1,188,000円です。` },
          { q: '仲介手数料が半額になる条件はありますか？', a: S.fees.conditionDetail.join('。') + '。' },
          { q: '川崎市と横浜市の中古マンション相場は？', a: '国土交通省の成約価格データを当社で集計すると、2025年の成約㎡単価（中央値）は川崎市全体で64.7万円、横浜市全体で51.7万円です。区別では川崎市中原区が104.3万円、横浜市西区が97.1万円と高くなっています。' },
          { q: '管理の状態はどう確認しますか？', a: '管理会社が作成する重要事項調査報告書、長期修繕計画、管理規約、総会議事録で、修繕積立金の残高と値上げの予定、滞納、大規模修繕の履歴と予定を確認します。' },
          { q: '旧耐震のマンションは避けたほうがよいですか？', a: '一概には言えませんが、1981年6月1日より前に建築確認を受けた建物は、耐震診断・改修の状況や住宅ローン減税の要件を確認する必要があります（要件は要確認）。' },
          { q: '来店は必要ですか？', a: '不要です。ご相談から契約手続きまでフォーム・LINE・オンラインで進めます。内見は現地でご案内します。' },
        ],
        relatedSlugs: ['musashikosugi-mansion-2021-2025', 'kawasaki-mansion-seiyaku-202608', 'kawasaki-tower-mansion-ku-betsu'],
        notes: [API_NOTICE_JA],
        ctaTitle: '中古マンション購入のご相談',
      },
    };
  }

  return {
    'chuko-mansion': {
      key: 'chuko-mansion',
      path: BUY_TYPE_PATH['chuko-mansion'].en,
      label: 'Resale condominiums',
      title: 'Buying a resale condominium in Kawasaki or Yokohama | Brokerage fee: half the legal maximum',
      description: `We help you buy a resale condominium in Kawasaki or Yokohama for a brokerage fee of ${S.fees.sale}. We check the price against public transaction data and the building’s management through its documents. Includes 2025 closed prices by ward. In English or Japanese.`,
      eyebrow: 'Resale Condominiums',
      lead: `We check the price against public transaction data and the building’s management through its documents before you decide. Our fee for buying a resale condominium, mainly in Kawasaki and Yokohama, is ${S.fees.sale}.`,
      serviceType: 'Brokerage for buying resale condominiums',
      sections: [
        {
          q: 'How much is the brokerage fee for a resale condominium?',
          a: `${S.fees.sale}. On a ¥70 million condominium that is ¥1,188,000 including tax, ¥1,188,000 less than the legal maximum (¥2,376,000).`,
          body: ['The rate is the same for every property. We do not add loan-processing or similar fees. The fee is charged only when a contract is concluded.'],
        },
        {
          q: 'What do resale condominiums cost in Kawasaki and Yokohama?',
          a: 'By our count of public transaction data from the Ministry of Land, Infrastructure, Transport and Tourism, the median closed price of resale condominiums in 2025 was ¥647,000 per square meter in Kawasaki and ¥517,000 in Yokohama. By ward, Nakahara in Kawasaki (home to Musashikosugi, ¥1,043,000) and Nishi in Yokohama (home to Minato Mirai, ¥971,000) were the highest.',
          table: {
            caption: 'Resale condominium closed prices per square meter in Kawasaki and Yokohama (2025, median by ward)',
            head: ['Area', 'Median price per m²', 'For 70 m²', 'Transactions'],
            rows: WARD_ROWS_EN,
            note: 'Source: our count based on the Real Estate Information Library (transaction prices) of the Ministry of Land, Infrastructure, Transport and Tourism. January to December 2025, resale condominiums. Not adjusted for building age or size; a rough guide to each ward’s level.',
          },
          body: ['Prices vary widely within a ward by distance from the station and building age. If you have a property in mind, we will look up closed prices in the same building and nearby and explain them.'],
          links: [
            { label: 'Have Musashikosugi resale condo prices overtaken central Tokyo? (article)', href: '/en/blog/musashikosugi-mansion-2021-2025/' },
            { label: 'Estimate a Kawasaki condo’s price instantly (valuation tool)', href: '/en/sell/valuation/' },
          ],
        },
        {
          q: 'How do you judge whether a price is fair?',
          a: 'We compare it with the public transaction data and with recent closed prices in the same building and nearby. The key is to compare with prices that actually closed, not asking prices.',
          body: ['Age, floor, orientation and renovation all affect the price, so we line up comparable cases. If the price looks high, you can use the comparison in negotiation.'],
        },
        {
          q: 'How do you check how the building is managed?',
          a: 'Through the management company’s report on important matters (juyo jiko chosa hokokusho), the long-term repair plan and the building rules. In Japan it is often said that when you buy a condominium you are buying its management.',
          list: [
            'Repair reserve contributions and balance, and any planned increases',
            'Unpaid management fees or reserve contributions across the building',
            'History of major repairs and when the next one is planned',
            'Minutes of the owners’ association meetings (disputes or large planned expenses)',
            'Building rules (restrictions on pets, renovation, short-term rentals and so on)',
          ],
        },
        {
          q: 'Is a low repair reserve a good thing?',
          a: 'Not necessarily. A small reserve can lead to a large increase later, or a lump-sum charge when major repairs are due.',
          body: ['We compare the amounts in the long-term repair plan with the current reserve to see whether it falls short. Another reference is the ministry’s guideline on repair reserves (figures to be confirmed).'],
        },
        {
          q: 'How should I read building age and the earthquake standard?',
          a: 'One benchmark is whether building confirmation was granted on or after June 1, 1981 (the "new" earthquake standard). We check the confirmation date, not just the year built.',
          body: ['For the mortgage tax deduction, homes built in 1982 or later are treated as meeting the new standard. Older buildings may qualify with an earthquake-resistance certificate (requirements to be confirmed).'],
        },
        {
          q: 'What should I watch for in a tower condominium, such as in Musashikosugi?',
          a: 'Beyond the view and shared facilities, check the level of management fees and repair reserves, and how the building is prepared for disasters.',
          body: ['In Typhoon Hagibis in 2019, basement electrical equipment flooded in some Musashikosugi tower condominiums, causing power and water outages. We check where the electrical equipment is, what flood measures exist and whether there is an emergency generator. Flood risk along the Tama River can be checked on the hazard maps.'],
          list: [
            'Management fees and repair reserves, and the expected cost of high-rise repairs (facade, elevators)',
            'Location of electrical equipment, flood measures, emergency power and elevators during outages',
            'Price differences by floor and orientation within the same building',
          ],
          links: [
            { label: 'Which ward of Kawasaki has the most tower condominiums? (article)', href: '/en/blog/kawasaki-tower-mansion-ku-betsu/' },
            { label: 'Hazard Map Portal Site (Ministry of Land, Infrastructure, Transport and Tourism)', href: 'https://disaportal.gsi.go.jp/', external: true },
          ],
        },
        {
          q: 'What should I check if I plan to renovate?',
          a: 'First check the building rules for restrictions on the work (floor sound insulation, moving the kitchen or bathroom), then estimate the cost during the viewing.',
          body: ['Budget for the purchase price plus renovation, and ask the bank whether renovation costs can be included in the mortgage.'],
        },
        {
          q: 'Can you handle a resale condominium I found on SUUMO?',
          a: 'Yes. Send us the link. Most properties for sale are shared among agencies through the industry database (REINS), so in principle we can submit an offer on your behalf.',
          body: ['Some listings are kept exclusively by the seller’s agent. We will check and tell you.'],
          links: [{ label: 'Found a property on SUUMO? Can another agency handle it? (article)', href: '/en/blog/portal-bukken-url-chukai/' }],
        },
      ],
      steps: [
        { title: 'Contact us', body: 'Send your preferred area, budget and timing, or a link to a property you like, via the form below or LINE.' },
        { title: 'Market prices and financing', body: 'We explain prices with transaction data and guide you on mortgage pre-approval.' },
        { title: 'Viewings and documents', body: 'We show you the property on site and check its management through the report on important matters and the repair plan.' },
        { title: 'Offer and contract', body: 'We negotiate price and conditions, then handle the explanation of important matters and the sales contract.' },
        { title: 'Settlement and handover', body: `Brokerage fee: ${S.fees.sale}. We support you through loan execution and registration.` },
      ],
      faq: [
        { q: 'How much is the brokerage fee for a resale condominium?', a: `${S.fees.sale}. On a ¥70 million property, ¥1,188,000 including tax, ¥1,188,000 less than the legal maximum.` },
        { q: 'Are there conditions for the half-price fee?', a: S.fees.conditionDetail.join('. ') + '.' },
        { q: 'What do resale condominiums cost in Kawasaki and Yokohama?', a: 'By our count of public transaction data, the 2025 median was ¥647,000 per square meter in Kawasaki and ¥517,000 in Yokohama. Nakahara Ward in Kawasaki (¥1,043,000) and Nishi Ward in Yokohama (¥971,000) were the highest.' },
        { q: 'How do you check the building’s management?', a: 'Through the report on important matters, the long-term repair plan, the building rules and meeting minutes: reserve balance and planned increases, arrears, and past and planned major repairs.' },
        { q: 'Should I avoid buildings under the old earthquake standard?', a: 'Not necessarily, but for buildings whose confirmation predates June 1, 1981, check the earthquake assessment and retrofitting, and the mortgage tax deduction requirements (to be confirmed).' },
        { q: 'Do I need to visit an office?', a: 'No. Consultations and paperwork are handled via form, LINE and online meetings. Viewings take place on site.' },
      ],
      relatedSlugs: ['musashikosugi-mansion-2021-2025', 'kawasaki-mansion-seiyaku-202608', 'kawasaki-tower-mansion-ku-betsu'],
      notes: [API_NOTICE_EN],
      ctaTitle: 'Ask about buying a resale condominium',
    },
  };
}
