/**
 * 目的別ページ（借りたい / 買いたい / 売りたい）の内容。日英。
 * ルール（CLAUDE.md）: 見出しは質問文、直後に結論。料金・会社情報は site.ts の値を使う。「無料」は使わない。法令は要確認と書く。
 */
import { siteFor } from '../config/site';
import type { Locale } from '../i18n';
import type { InquiryType } from './contact-fields';

export type PurposeKey = Extract<InquiryType, 'rent' | 'buy' | 'sell'>;
export const PURPOSE_KEYS: readonly PurposeKey[] = ['rent', 'buy', 'sell'];

export interface Section {
  /** 質問文の見出し */
  q: string;
  /** 結論（太字で先頭に出す） */
  a: string;
  /** 補足段落（任意） */
  body?: string[];
  /** 箇条書き（任意） */
  list?: string[];
}

export interface PurposeContent {
  key: PurposeKey;
  path: string;
  /** ナビやカードで使う短い名前 */
  label: string;
  /** <title> と h1 */
  title: string;
  /** meta description（結論を含める） */
  description: string;
  eyebrow: string;
  lead: string;
  sections: Section[];
  steps: { title: string; body: string }[];
  faq: { q: string; a: string }[];
  /** ページ末尾の CTA 見出し */
  ctaTitle: string;
}

export function getPurposePages(locale: Locale): Record<PurposeKey, PurposeContent> {
  const S = siteFor(locale);
  const ja = locale === 'ja';
  const p = (path: string) => (ja ? path : `/en${path}`);

  if (ja) {
    return {
      rent: {
        key: 'rent',
        path: p('/rent/'),
        label: '借りたい',
        title: '賃貸を借りたい方へ｜仲介手数料は家賃の半額',
        description: `賃貸のお部屋探しは、仲介手数料${S.fees.rent}で承ります。東京・神奈川を中心に一都3県に対応。ポータルサイトで見つけた物件の持ち込みも歓迎です。来店不要で、ご相談と契約手続きはフォーム・LINE・オンライン、内見は現地でご案内します。`,
        eyebrow: 'For Tenants',
        lead: `お部屋探しの仲介手数料は${S.fees.rent}です。一般的な「家賃1ヶ月分＋税」の半分で、初期費用を抑えられます。`,
        sections: [
          {
            q: '賃貸の仲介手数料はいくらですか？',
            a: `${S.fees.rent}です。家賃15万円なら 82,500円（税込）で、一般的な1ヶ月分＋税（165,000円）との差は 82,500円になります。`,
            body: ['金額は物件によらず同じ率です。手数料以外の名目（事務手数料、書類作成費など）はいただきません。費用が発生するのは成約時のみで、ご相談の段階では費用はかかりません。'],
          },
          {
            q: 'ポータルサイトで見つけた物件も頼めますか？',
            a: 'はい。SUUMO や HOME’S などで見つけた物件の URL をお送りください。多くの物件は不動産会社どうしの情報網で共有されていますので、原則として当社からも申し込めます。',
            body: ['一部に、掲載している会社だけで扱う物件もあります。その場合はその旨をお伝えし、近い条件の物件をご提案します。'],
          },
          {
            q: 'どのエリアに対応していますか？',
            a: '東京・神奈川を中心に、千葉・埼玉を含む一都3県に対応しています。武蔵小杉、元住吉、新丸子など東急東横線沿線と、川崎・横浜のタワーマンションは特に土地勘があります。',
          },
          {
            q: '来店せずに契約までできますか？',
            a: 'はい。ご相談、ヒアリング、申込、重要事項説明、契約の手続きはフォーム・LINE・オンラインで進めます。内見だけは現地でお待ち合わせしてご案内します。',
            body: ['重要事項説明をオンラインで行う「IT重説」は、法令上の要件を満たす方法で実施します（実施方法の詳細は要確認事項を含みますので、事前にご案内します）。'],
          },
          {
            q: '外国籍でも借りられますか？',
            a: 'はい。英語でのご相談に対応しています。物件によって受け入れの条件が異なりますので、在留資格や入居時期を早めにお知らせいただくと、候補を絞りやすくなります。',
            body: ['契約書と重要事項説明書は日本語が正本で、英訳は参考資料としてご用意し、内容は英語でご説明します。'],
          },
        ],
        steps: [
          { title: 'お問い合わせ', body: '希望エリア・家賃・間取り・入居時期を、下のフォームか LINE でお送りください。' },
          { title: '物件のご提案', body: '条件に合う物件を複数ご紹介します。気になる物件の持ち込みも歓迎です。' },
          { title: '内見', body: '現地でお待ち合わせし、実際にお部屋をご確認いただきます。' },
          { title: '申込・審査', body: '入居申込と保証会社の審査を進めます。必要書類はその時点でご案内します。' },
          { title: '契約・お引渡し', body: `仲介手数料は${S.fees.rent}。鍵のお引渡しまでサポートします。` },
        ],
        faq: [
          { q: '賃貸の仲介手数料はいくらですか？', a: `${S.fees.rent}です。家賃15万円なら82,500円（税込）で、一般的な家賃1ヶ月分＋税との差は82,500円です。手数料以外の名目の費用はいただきません。` },
          { q: 'ポータルサイトで見つけた物件を仲介してもらえますか？', a: 'はい。物件の URL をお送りください。多くの物件は不動産会社どうしで共有されていますので、原則として当社からも申し込めます。一部に扱えない物件もあり、その場合はお伝えします。' },
          { q: '来店は必要ですか？', a: '不要です。ご相談から契約手続きまでフォーム・LINE・オンラインで進めます。内見は現地でお待ち合わせしてご案内します。' },
          { q: '対応エリアはどこですか？', a: '東京・神奈川を中心に、千葉・埼玉を含む一都3県です。武蔵小杉や東急東横線沿線、川崎・横浜のタワーマンションは特に詳しくご案内できます。' },
          { q: '外国籍でも相談できますか？', a: 'はい。英語で対応します。契約書と重要事項説明書は日本語が正本で、英訳を参考資料としてご用意します。' },
        ],
        ctaTitle: 'お部屋探しのご相談',
      },
      buy: {
        key: 'buy',
        path: p('/buy/'),
        label: '買いたい',
        title: '住まいを買いたい方へ｜仲介手数料は法定上限の半額',
        description: `マンション・一戸建て・土地の購入を、仲介手数料${S.fees.sale}で仲介します。東京・神奈川を中心に一都3県に対応。7,000万円の物件なら、法定上限との差は約119万円です。来店不要で、ご相談と契約手続きはオンライン、内見は現地でご案内します。`,
        eyebrow: 'For Buyers',
        lead: `購入の仲介手数料は${S.fees.sale}です。${S.fees.saleNote}ですので、価格が高い物件ほど差が大きくなります。`,
        sections: [
          {
            q: '購入時の仲介手数料はいくらですか？',
            a: `${S.fees.sale}です。7,000万円の物件なら 1,188,000円（税込）で、法定上限（2,376,000円）との差は 1,188,000円になります。`,
            body: ['率は物件によらず同じです。ローン事務代行手数料などの名目の費用はいただきません。費用が発生するのは成約時のみです。'],
          },
          {
            q: '気になる物件があれば、その物件を仲介してもらえますか？',
            a: 'はい。ポータルサイトや他社サイトで見つけた物件の URL をお送りください。売買物件の多くは不動産会社どうしの情報網（レインズ）で共有されていますので、原則として当社から購入の申込ができます。',
            body: ['売主側の会社だけで扱う物件（いわゆる囲い込み）もありますので、その場合は確認のうえお伝えします。'],
          },
          {
            q: '住宅ローンの相談もできますか？',
            a: 'はい。購入の流れの中で、事前審査のタイミングや必要書類をご案内します。金融機関の選定はお客様のご希望を優先し、特定の金融機関をおすすめすることはありません。',
          },
          {
            q: '中古マンションの価格が適正か、どう判断しますか？',
            a: '国土交通省が公開している成約価格の公的データと、周辺の販売事例を照らし合わせてご説明します。川崎・横浜のタワーマンションについては、ブログで四半期ごとに成約価格の動きを整理しています。',
          },
          {
            q: '来店せずに購入まで進められますか？',
            a: 'はい。ご相談、資金計画、購入申込、重要事項説明、契約の手続きはフォーム・LINE・オンラインで進めます。内見は現地でご案内し、決済・引渡しは金融機関や司法書士と日程を調整して行います。',
            body: ['重要事項説明をオンラインで行う「IT重説」は、法令上の要件を満たす方法で実施します（実施方法の詳細は要確認事項を含みますので、事前にご案内します）。'],
          },
        ],
        steps: [
          { title: 'お問い合わせ', body: '希望エリア・物件種別・予算・時期を、下のフォームか LINE でお送りください。' },
          { title: '資金計画とご提案', body: 'ご予算に合わせて物件をご提案します。住宅ローンの事前審査のタイミングもご案内します。' },
          { title: '内見', body: '現地でお待ち合わせし、物件と周辺環境をご確認いただきます。' },
          { title: '購入申込・契約', body: '価格や条件の交渉、重要事項説明、売買契約を進めます。' },
          { title: '決済・お引渡し', body: `仲介手数料は${S.fees.sale}。ローン実行と登記手続きまでサポートします。` },
        ],
        faq: [
          { q: '購入時の仲介手数料はいくらですか？', a: `${S.fees.sale}です。7,000万円の物件なら1,188,000円（税込）で、法定上限との差は1,188,000円です。ローン事務代行手数料などの名目の費用はいただきません。` },
          { q: '他社サイトで見つけた物件も仲介してもらえますか？', a: 'はい。物件の URL をお送りください。多くの売買物件は不動産会社どうしで共有されていますので、原則として当社から申込ができます。売主側の会社だけで扱う物件もあり、その場合はお伝えします。' },
          { q: '住宅ローンの相談はできますか？', a: 'はい。事前審査のタイミングや必要書類をご案内します。金融機関はお客様のご希望を優先して選びます。' },
          { q: '来店は必要ですか？', a: '不要です。ご相談から契約手続きまでフォーム・LINE・オンラインで進めます。内見は現地でご案内します。' },
          { q: '外国籍でも購入できますか？', a: 'はい。日本では国籍を問わず不動産を購入できます。英語でご説明し、契約書は日本語が正本で英訳を参考資料としてご用意します。住宅ローンの条件は金融機関によって異なりますので、要確認事項として早めにご相談ください。' },
        ],
        ctaTitle: '購入のご相談',
      },
      sell: {
        key: 'sell',
        path: p('/sell/'),
        label: '売りたい',
        title: '住まいを売りたい方へ｜仲介手数料は法定上限の半額',
        description: `マンション・一戸建て・土地の売却を、仲介手数料${S.fees.sale}で仲介します。東京・神奈川を中心に一都3県に対応。国土交通省の成約価格データにもとづく査定を、費用をいただかずに行います。来店不要で、ご相談と契約手続きはオンラインで進めます。`,
        eyebrow: 'For Sellers',
        lead: `売却の仲介手数料は${S.fees.sale}です。7,000万円で売れた場合、法定上限との差は 1,188,000円になります。`,
        sections: [
          {
            q: '売却時の仲介手数料はいくらですか？',
            a: `${S.fees.sale}です。${S.fees.saleNote}ですので、7,000万円の売却なら 1,188,000円（税込）で、上限との差は 1,188,000円です。`,
            body: ['手数料は成約時にのみ発生します。査定やご相談の段階で費用はかかりません。'],
          },
          {
            q: '査定はどのように行いますか？',
            a: '国土交通省が公開している成約価格の公的データと、周辺の販売事例、物件の状態をもとに、売り出し価格の目安と想定される成約価格の幅をご説明します。',
            body: ['「高い査定額を出して媒介契約を取る」ことはしません。根拠となるデータをそのままお見せします。'],
          },
          {
            q: '媒介契約の種類はどれがよいですか？',
            a: '専任媒介・専属専任媒介・一般媒介の3種類があり、それぞれ報告義務やレインズへの登録義務が異なります。ご事情に合わせてご説明しますので、内容を理解したうえでお選びください（各契約の法令上の扱いは要確認事項を含みます）。',
          },
          {
            q: '売却活動では何をしますか？',
            a: 'レインズとポータルサイトへの掲載、写真撮影、内見の立ち会い、購入希望者との条件交渉、契約書類の作成、決済・引渡しの調整までを一貫して行います。',
            body: ['自社の買主に限定して売る「囲い込み」は行いません。他社経由の購入希望者にも同じ条件でご案内します。'],
          },
          {
            q: '住みながら売却できますか？',
            a: 'はい。内見は事前に日程を調整し、当社が立ち会います。空室にしてからの売却と、住みながらの売却のどちらが有利かは物件によりますので、ご相談のうえ決めます。',
          },
        ],
        steps: [
          { title: 'お問い合わせ', body: '物件の所在地・種別・売却の時期感を、下のフォームか LINE でお送りください。' },
          { title: '査定', body: '公的な成約価格データと周辺事例をもとに、価格の目安をご説明します。' },
          { title: '媒介契約・売り出し', body: '契約の種類をご説明のうえ、レインズとポータルサイトに掲載します。' },
          { title: '内見対応・交渉', body: '内見に立ち会い、購入希望者との条件交渉を行います。' },
          { title: '契約・決済・お引渡し', body: `仲介手数料は${S.fees.sale}。契約から引渡しまでサポートします。` },
        ],
        faq: [
          { q: '売却時の仲介手数料はいくらですか？', a: `${S.fees.sale}です。7,000万円の売却なら1,188,000円（税込）で、法定上限との差は1,188,000円です。費用が発生するのは成約時のみです。` },
          { q: '査定に費用はかかりますか？', a: 'かかりません。国土交通省の成約価格データと周辺事例をもとに、根拠を示してご説明します。' },
          { q: '囲い込みはしませんか？', a: 'しません。他社経由の購入希望者にも同じ条件でご案内し、レインズにも登録します。' },
          { q: '住みながら売れますか？', a: 'はい。内見は日程を調整し、当社が立ち会います。' },
          { q: '来店は必要ですか？', a: '不要です。ご相談から媒介契約、売買契約までフォーム・LINE・オンラインで進めます。査定のための現地確認と内見の立ち会いは現地で行います。' },
        ],
        ctaTitle: '売却・査定のご相談',
      },
    };
  }

  return {
    rent: {
      key: 'rent',
      path: p('/rent/'),
      label: 'Rent',
      title: 'Renting a home | Brokerage fee: half a month’s rent',
      description: `Rental brokerage for ${S.fees.rent}. Serving Tokyo, Kanagawa, Chiba and Saitama, in English or Japanese. Bring us a listing you found on a portal site. No office visit needed: consultations and paperwork online, viewings on site.`,
      eyebrow: 'For Tenants',
      lead: `Our rental brokerage fee is ${S.fees.rent}, half the usual one month plus tax, which lowers your move-in costs.`,
      sections: [
        {
          q: 'How much is the brokerage fee for a rental?',
          a: `${S.fees.rent}. For a ¥150,000 apartment that is ¥82,500 including tax, ¥82,500 less than the usual one month plus tax (¥165,000).`,
          body: ['The rate is the same for every property. We do not add administrative or document fees. The fee is charged only when a contract is concluded.'],
        },
        {
          q: 'Can you handle a listing I found on a portal site?',
          a: 'Yes. Send us the link. Most listings are shared among agencies, so in principle we can apply for the same apartment.',
          body: ['A few listings are handled only by the advertising agency. If so, we will tell you and propose similar options.'],
        },
        {
          q: 'Which areas do you cover?',
          a: 'Tokyo and Kanagawa first, plus Chiba and Saitama. We know the Tokyu Toyoko line (Musashikosugi, Motosumiyoshi, Shinmaruko) and the tower condominiums of Kawasaki and Yokohama particularly well.',
        },
        {
          q: 'Can I rent without visiting an office?',
          a: 'Yes. Consultations, the application, the explanation of important matters and the contract are handled via form, LINE and online meetings. Viewings take place on site with us.',
          body: ['Online explanations of important matters are conducted in a way that meets the legal requirements; we will explain the procedure in advance, as some points require confirmation case by case.'],
        },
        {
          q: 'Can non-Japanese residents rent through you?',
          a: 'Yes. We work in English. Acceptance conditions vary by property, so telling us your residence status and move-in date early helps us shortlist.',
          body: ['The Japanese contract and explanation of important matters are the binding documents; we provide English translations for reference and explain everything in English.'],
        },
      ],
      steps: [
        { title: 'Contact us', body: 'Send your preferred area, rent, layout and move-in date via the form below or LINE.' },
        { title: 'Proposals', body: 'We shortlist matching apartments. Listings you found yourself are welcome.' },
        { title: 'Viewings', body: 'We meet you on site and view the apartments together.' },
        { title: 'Application and screening', body: 'We handle the application and the guarantor company screening, and tell you which documents are needed.' },
        { title: 'Contract and keys', body: `Brokerage fee: ${S.fees.rent}. We support you through to key handover.` },
      ],
      faq: [
        { q: 'How much is the rental brokerage fee?', a: `${S.fees.rent}. For a ¥150,000 apartment, ¥82,500 including tax, which is ¥82,500 less than the usual one month plus tax. No administrative or document fees.` },
        { q: 'Can you apply for a listing I found on a portal site?', a: 'Yes. Send the link. Most listings are shared among agencies, so in principle we can apply. A few are exclusive to one agency; we will tell you if so.' },
        { q: 'Do I need to visit an office?', a: 'No. Consultations and paperwork are handled via form, LINE and online meetings. Viewings take place on site with us.' },
        { q: 'Which areas do you cover?', a: 'Tokyo and Kanagawa first, plus Chiba and Saitama. Musashikosugi, the Tokyu Toyoko line and the tower condominiums of Kawasaki and Yokohama are our strongest areas.' },
        { q: 'Do you work in English?', a: 'Yes. The Japanese contract is the binding document; we provide English translations for reference and explain everything in English.' },
      ],
      ctaTitle: 'Ask about renting',
    },
    buy: {
      key: 'buy',
      path: p('/buy/'),
      label: 'Buy',
      title: 'Buying a home | Brokerage fee: half the legal maximum',
      description: `Buy a condominium, house or land with a brokerage fee of ${S.fees.sale}. Serving Tokyo, Kanagawa, Chiba and Saitama, in English or Japanese. On a ¥70 million property the saving versus the legal maximum is about ¥1.19 million. Consultations and paperwork online, viewings on site.`,
      eyebrow: 'For Buyers',
      lead: `Our fee for purchases is ${S.fees.sale}. Since ${S.fees.saleNote}, the saving grows with the price.`,
      sections: [
        {
          q: 'How much is the brokerage fee when buying?',
          a: `${S.fees.sale}. On a ¥70 million property that is ¥1,188,000 including tax, ¥1,188,000 less than the legal maximum (¥2,376,000).`,
          body: ['The rate is the same for every property. We do not add loan-processing or similar fees. The fee is charged only when a contract is concluded.'],
        },
        {
          q: 'Can you handle a property I found elsewhere?',
          a: 'Yes. Send us the link. Most properties for sale are shared among agencies through the industry database (REINS), so in principle we can submit an offer on your behalf.',
          body: ['Some listings are kept exclusively by the seller’s agent. We will check and tell you.'],
        },
        {
          q: 'Can you help with a mortgage?',
          a: 'Yes. We guide you on when to apply for pre-approval and which documents are needed. Your choice of bank comes first; we do not push a particular lender.',
          body: ['For non-Japanese residents, mortgage conditions vary by bank and residence status, so please raise this early.'],
        },
        {
          q: 'How do you judge whether a price is fair?',
          a: 'We compare it with the public transaction-price data published by Japan’s Ministry of Land, Infrastructure, Transport and Tourism and with nearby listings. For the tower condominiums of Kawasaki and Yokohama we publish a quarterly review on the blog.',
        },
        {
          q: 'Can I buy without visiting an office?',
          a: 'Yes. Consultations, financing, the offer, the explanation of important matters and the contract are handled via form, LINE and online meetings. Viewings take place on site; settlement and handover are scheduled with the bank and the judicial scrivener.',
          body: ['Online explanations of important matters are conducted in a way that meets the legal requirements; we will explain the procedure in advance.'],
        },
      ],
      steps: [
        { title: 'Contact us', body: 'Send your preferred area, property type, budget and timing via the form below or LINE.' },
        { title: 'Financing and proposals', body: 'We propose properties within your budget and guide you on mortgage pre-approval.' },
        { title: 'Viewings', body: 'We meet you on site and check the property and the neighborhood together.' },
        { title: 'Offer and contract', body: 'We negotiate price and conditions, then handle the explanation of important matters and the sales contract.' },
        { title: 'Settlement and handover', body: `Brokerage fee: ${S.fees.sale}. We support you through loan execution and registration.` },
      ],
      faq: [
        { q: 'How much is the brokerage fee when buying?', a: `${S.fees.sale}. On a ¥70 million property, ¥1,188,000 including tax, ¥1,188,000 less than the legal maximum. No loan-processing fees.` },
        { q: 'Can you handle a listing from another agency’s website?', a: 'Yes. Send the link. Most properties are shared among agencies, so in principle we can submit an offer. Some are exclusive to the seller’s agent; we will tell you if so.' },
        { q: 'Can foreigners buy property in Japan?', a: 'Yes. There is no nationality restriction on owning property in Japan. Mortgage conditions vary by bank and residence status, so please confirm early. We explain everything in English; the Japanese contract is the binding document.' },
        { q: 'Do I need to visit an office?', a: 'No. Consultations and paperwork are handled via form, LINE and online meetings. Viewings take place on site.' },
        { q: 'Can you help with a mortgage?', a: 'Yes. We guide you on pre-approval timing and documents. Your choice of bank comes first.' },
      ],
      ctaTitle: 'Ask about buying',
    },
    sell: {
      key: 'sell',
      path: p('/sell/'),
      label: 'Sell',
      title: 'Selling your home | Brokerage fee: half the legal maximum',
      description: `Sell a condominium, house or land with a brokerage fee of ${S.fees.sale}. Serving Tokyo, Kanagawa, Chiba and Saitama. Valuations are based on public transaction data and cost nothing. Consultations and paperwork online.`,
      eyebrow: 'For Sellers',
      lead: `Our fee for sales is ${S.fees.sale}. If your home sells for ¥70 million, the saving versus the legal maximum is ¥1,188,000.`,
      sections: [
        {
          q: 'How much is the brokerage fee when selling?',
          a: `${S.fees.sale}. Since ${S.fees.saleNote}, a ¥70 million sale costs ¥1,188,000 including tax, ¥1,188,000 less than the maximum.`,
          body: ['The fee is charged only when the sale is concluded. Valuations and consultations cost nothing.'],
        },
        {
          q: 'How do you value my property?',
          a: 'We use the public transaction-price data published by the Ministry of Land, Infrastructure, Transport and Tourism, nearby listings and the condition of your property to explain a suggested asking price and the likely range of the final price.',
          body: ['We do not inflate valuations to win the listing. You see the underlying data.'],
        },
        {
          q: 'Which type of listing agreement should I choose?',
          a: 'There are three types in Japan (exclusive, exclusive with restrictions, and general), with different reporting and REINS registration duties. We explain each so you can choose with full understanding; some legal points require confirmation case by case.',
        },
        {
          q: 'What do you do to sell the property?',
          a: 'Listing on REINS and portal sites, photography, accompanying viewings, negotiating with buyers, preparing contract documents, and coordinating settlement and handover.',
          body: ['We do not hide your listing from other agencies to keep both sides of the deal. Buyers introduced by other agencies are welcome on the same terms.'],
        },
        {
          q: 'Can I sell while still living there?',
          a: 'Yes. Viewings are scheduled in advance and we attend each one. Whether to sell vacant or occupied depends on the property; we decide together.',
        },
      ],
      steps: [
        { title: 'Contact us', body: 'Send the location, property type and your timing via the form below or LINE.' },
        { title: 'Valuation', body: 'We explain a price range based on public transaction data and nearby listings.' },
        { title: 'Listing agreement and marketing', body: 'We explain the agreement types, then list on REINS and portal sites.' },
        { title: 'Viewings and negotiation', body: 'We attend viewings and negotiate with prospective buyers.' },
        { title: 'Contract, settlement, handover', body: `Brokerage fee: ${S.fees.sale}. We support you through to handover.` },
      ],
      faq: [
        { q: 'How much is the brokerage fee when selling?', a: `${S.fees.sale}. For a ¥70 million sale, ¥1,188,000 including tax, ¥1,188,000 less than the legal maximum. Charged only when the sale is concluded.` },
        { q: 'Does a valuation cost anything?', a: 'No. We base it on public transaction data and nearby listings, and show you the data.' },
        { q: 'Do you hide listings from other agencies?', a: 'No. We register the property on REINS and welcome buyers from other agencies on the same terms.' },
        { q: 'Can I sell while living in the property?', a: 'Yes. Viewings are scheduled in advance and we attend them.' },
        { q: 'Do I need to visit an office?', a: 'No. Consultations, the listing agreement and the sales contract are handled via form, LINE and online meetings. The valuation visit and viewings take place on site.' },
      ],
      ctaTitle: 'Ask about selling',
    },
  };
}
