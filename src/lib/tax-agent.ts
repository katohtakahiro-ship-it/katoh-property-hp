/**
 * 納税管理人ページ（/nozei-kanrinin/ ・ /en/tax-agent/）の内容。日英。
 * ルール（CLAUDE.md）: 見出しは質問文、直後に結論。「無料」は使わない。法令は要確認と書く。
 * 範囲（2026-11-05 決定）: 届出・書類の受け取りと転送・期限のお知らせ・お預かりした資金での納付。
 * 申告書の作成・提出、税額の計算、税務相談は引き受けない（税理士法）。税理士の紹介もしない（提携先なし）。
 * 料金は年 US$200。円で受け取るのは海外在住の日本人の方だけ（換算はステーブルコインと同じ、請求書の発行日のみずほ銀行 TTM）。
 * 消費税はかかるものとして扱うが、ページ・記事では触れない（US$200 は総額）。
 */
import type { Locale } from '../i18n';
import type { Section } from './purpose-pages';

export const TAX_AGENT_PATH: Record<Locale, string> = {
  ja: '/nozei-kanrinin/',
  en: '/en/tax-agent/',
};

export const TAX_AGENT_FEE_USD = 200;

export interface TaxAgentContent {
  path: string;
  label: string;
  title: string;
  h1: string;
  description: string;
  eyebrow: string;
  lead: string;
  priceLabel: string;
  price: string;
  priceNote: string;
  doLabel: string;
  doList: string[];
  dontLabel: string;
  dontList: string[];
  sections: Section[];
  steps: { title: string; body: string }[];
  faq: { q: string; a: string }[];
  ctaTitle: string;
  articleSlug: string;
}

export function getTaxAgentPage(locale: Locale): TaxAgentContent {
  if (locale === 'ja') {
    return {
      path: TAX_AGENT_PATH.ja,
      label: '納税管理人',
      title: '海外赴任・海外在住の方の納税管理人をお引き受けします（年200ドル）',
      h1: '海外にお住まいの方の納税管理人',
      description:
        '海外赴任・海外移住などで日本に住所がなくなる方の納税管理人を、年 US$200 でお引き受けします。税務署・市区町村・都道府県への届出、税金の書類の受け取りと PDF での転送、期限のお知らせ、お預かりした資金での納付を行います。物件は日本全国が対象です。申告書の作成・提出と税務相談はお受けしていません。',
      eyebrow: 'Tax Agent Service',
      lead: '海外赴任や移住で日本を離れても、日本の家や土地には毎年税金がかかります。税金の書類を日本で受け取り、期限までに納める窓口として、当社が納税管理人になります。',
      priceLabel: '料金',
      price: '年 US$200',
      priceNote: '1年分を前払い。Wise（米ドル）・USDC のほか、海外にお住まいの日本人の方は日本円でもお支払いいただけます。',
      doLabel: '当社が行うこと',
      doList: [
        '税務署・市区町村・都道府県への納税管理人の届出（申告）の提出',
        '税金の書類の受け取りと、PDF での転送（書類の名前と期限を添えます）',
        '納付期限の前のお知らせ',
        'お預かりした資金での税金の納付と、領収書の転送',
        'ご帰国やご契約の終了のときの、納税管理人の解任の届出',
      ],
      dontLabel: '当社が行わないこと',
      dontList: ['確定申告書などの作成と提出', '税額の計算', '節税などの税務相談', '税金の立て替え'],
      sections: [
        {
          q: '納税管理人とは何ですか？',
          a: '日本に住所がない方に代わって、税務署や役所からの書類を受け取り、税金を納める国内の窓口です。',
          body: [
            '日本に住所も居所もない方が、日本で税金の手続きをする必要があるときは、納税管理人を定めて届け出ることとされています（国税は国税通則法117条、固定資産税などの地方税は地方税法）。届出先は、所得税などの国税は税務署、固定資産税は物件のある市区町村（東京23区は都税事務所）、不動産取得税は都道府県です。',
            '納税管理人になるのに資格はいりません。ご家族や知人にも頼めますし、当社のような法人でもなれます。具体的な要件や届出の様式は、税務署・自治体ごとにご確認いただく部分があります（要確認）。',
          ],
        },
        {
          q: 'どんな方が対象ですか？',
          a: '海外赴任・海外移住・留学などで日本に住所がなくなる方、すでに海外にお住まいの方で、日本に不動産をお持ちの方が対象です。物件は日本全国どこでもお引き受けします。',
          body: [
            'これから出国される方は、出国前にご相談ください。所得税の納税管理人を出国前に届け出ておくと、家賃収入などの確定申告を、出国の時ではなく通常どおり翌年の申告期限までに行えます（要確認）。',
          ],
        },
        {
          q: '確定申告もお願いできますか？',
          a: 'お受けしていません。申告書の作成・提出、税額の計算、税務相談は、税理士でなければ行えない業務とされているためです（税理士法）。',
          body: [
            '家賃収入があって確定申告が必要な方は、ご自身で申告するか、税理士にご依頼ください。税務署から届いた申告の書類は、当社から PDF で転送します。',
          ],
        },
        {
          q: '税金はどうやって納めるのですか？',
          a: '口座振替を使える税金は、ご本人の日本の口座から引き落とします。それ以外は、納める額を事前に当社にお送りいただき、当社が期限までに納めます。',
          body: [
            '当社が税金を立て替えることはありません。納税の義務はご本人にあり、資金が届かずに納付が遅れた場合の延滞金などは、ご本人のご負担になります。お預かりした資金は、税金の納付だけに使います。',
          ],
        },
        {
          q: '日本の家の貸し出しや売却も相談できますか？',
          a: 'ご相談いただけます。納税管理人のご契約とは別のご依頼で、当社に頼むかどうかは自由です。',
          list: [
            '住まいの購入・売却の仲介：東京・神奈川・千葉・埼玉の物件',
            '借主の募集（お部屋を貸したいオーナー様）：川崎市中原区・幸区・川崎区の物件',
          ],
        },
      ],
      steps: [
        { title: 'お問い合わせ', body: 'フォームか LINE で、お住まいの国、物件の所在地、届いている税金をお知らせください。' },
        { title: 'オンライン面談と本人確認', body: 'オンラインでお話を伺い、パスポートなどでご本人を確認します。どの税金の届出が必要かを一緒に整理します。' },
        { title: 'ご契約とお支払い', body: '委任契約を結び、1年分の料金（US$200）をお支払いいただきます。' },
        { title: '届出', body: '届出書をご用意し、ご署名をいただいた後、当社が税務署・市区町村・都道府県に提出します。' },
        { title: '書類の転送と納付', body: '届いた書類は、原則として受け取りから3営業日以内に PDF でお送りします。納付をお任せいただく税金は、期限までに当社が納めます。' },
        { title: '更新・終了', body: '1年ごとに更新します。ご帰国や物件の売却で不要になったときは、当社が解任の届出を提出します。' },
      ],
      faq: [
        {
          q: '納税管理人は家族に頼んでもいいですか？',
          a: '頼めます。資格はいりません。ご家族の転居やご高齢で続けにくくなった場合、ご家族に税金の書類を見られたくない場合などに、当社のような法人にお任せいただく方が多いと考えています。',
        },
        {
          q: '料金はいくらですか？ 円でも払えますか？',
          a: '年 US$200 で、1年分を前払いでお支払いいただきます。Wise（米ドル）か USDC でお支払いください。海外にお住まいの日本人の方は、日本円の振込でもお支払いいただけます。円の額は、請求書の発行日にみずほ銀行が公表する米ドルの対顧客電信仲値（TTM）で換算します（円未満切り捨て）。送金手数料はお客様のご負担です。',
        },
        {
          q: '確定申告の書類を作ってもらえますか？',
          a: 'お受けしていません。申告書の作成・提出と税務相談は、税理士でなければ行えない業務とされています。ご自身で申告するか、税理士にご依頼ください。',
        },
        {
          q: '税金を払えなかった場合、当社が代わりに払いますか？',
          a: 'いいえ。納税の義務はご本人にあり、当社が立て替えたり負担したりすることはありません。納付をお任せいただく税金は、事前に資金をお送りいただいた分だけ納めます。',
        },
        {
          q: '出国した後からでも頼めますか？',
          a: '頼めます。ただ、所得税の納税管理人は出国前に届け出ておくと手続きが少なく済むため（要確認）、出国が決まった段階でご相談いただくのがおすすめです。',
        },
        {
          q: '物件がどこにあっても頼めますか？',
          a: '日本全国の物件をお引き受けします。書類の受け取りと納付は郵送やオンラインで行えるため、物件の場所によって料金は変わりません。',
        },
      ],
      ctaTitle: '納税管理人について相談する',
      articleSlug: 'nozei-kanrinin',
    };
  }

  return {
    path: TAX_AGENT_PATH.en,
    label: 'Tax agent',
    title: 'Tax Agent (Nozei Kanrinin) for Property Owners Living Outside Japan | US$200/year',
    h1: 'Tax agent for owners living outside Japan',
    description:
      'If you own a home in Japan but do not live here, you generally need a tax agent (nozei kanrinin) in Japan. We act as your tax agent for US$200 a year: we file the appointment with the tax office and local governments, receive your tax notices and send them to you as PDFs, remind you of deadlines and pay the taxes from funds you send us. Properties anywhere in Japan. We do not prepare tax returns or give tax advice.',
    eyebrow: 'Tax Agent Service',
    lead: 'A holiday home or an investment property in Japan comes with Japanese tax bills, sent in Japanese to an address in Japan. We act as your tax agent: the local contact who receives those notices and pays the taxes on time.',
    priceLabel: 'Fee',
    price: 'US$200 a year',
    priceNote: 'Paid one year in advance, by Wise (US dollars) or USDC.',
    doLabel: 'What we do',
    doList: [
      'File the tax agent appointment with the tax office, the city or ward office, and the prefecture',
      'Receive your tax notices and send them to you as PDFs, with a short note in English on what each one is and when it is due',
      'Remind you before payment deadlines',
      'Pay the taxes from funds you send us, and send you the receipts',
      'File the termination of the appointment when you no longer need us',
    ],
    dontLabel: 'What we do not do',
    dontList: ['Prepare or file tax returns', 'Calculate your tax', 'Give tax advice or tax planning', 'Pay taxes out of our own funds'],
    sections: [
      {
        q: 'What is a tax agent (nozei kanrinin)?',
        a: 'A person or company in Japan that receives tax notices and pays Japanese taxes on behalf of someone who does not live in Japan.',
        body: [
          'If you have no address or residence in Japan but need to deal with Japanese taxes, Japanese law generally expects you to appoint a tax agent and notify the authorities (Article 117 of the Act on General Rules for National Taxes for national taxes, and the Local Tax Act for fixed asset tax and other local taxes). Income tax goes to the tax office, fixed asset tax to the city or ward where the property is (the Tokyo Metropolitan Tax Office in the 23 wards), and real estate acquisition tax to the prefecture.',
          'In some countries "tax agent" means a licensed tax accountant. A nozei kanrinin is not: no licence is needed, and a friend, a relative or a company can act as one. The exact requirements and forms vary between offices and are worth confirming case by case.',
        ],
      },
      {
        q: 'Who is this service for?',
        a: 'Anyone who owns, or is about to buy, property in Japan and lives outside Japan, whatever your nationality. We take on properties anywhere in Japan.',
        body: [
          'The best time to appoint us is around the purchase. The real estate acquisition tax notice usually arrives a few months after the property is registered, and fixed asset tax notices follow every year.',
        ],
      },
      {
        q: 'Can you file my Japanese tax return?',
        a: 'No. In Japan, preparing and filing tax returns, calculating tax and giving tax advice are reserved for licensed tax accountants (zeirishi).',
        body: [
          'If you rent the property out and need to file a return, please file it yourself or hire a licensed tax accountant. We forward any return forms the tax office sends.',
        ],
      },
      {
        q: 'How are the taxes paid?',
        a: 'You send us the amount due in advance, and we pay it before the deadline. If you have a Japanese bank account, taxes that allow direct debit can be paid from it instead.',
        body: [
          'We never pay taxes out of our own funds. You remain the taxpayer, so late-payment charges caused by funds arriving late are yours. Funds you send us are used only to pay your taxes.',
        ],
      },
      {
        q: 'Can you also help me buy a home in Japan?',
        a: 'Yes, as a separate engagement from the tax agent service. We broker purchases in Tokyo, Kanagawa, Chiba and Saitama, in English or Japanese.',
      },
    ],
    steps: [
      { title: 'Get in touch', body: 'Use the form or LINE. Tell us where you live, where the property is, and which tax notices you have received or expect.' },
      { title: 'Online meeting and ID check', body: 'We talk online, check your passport, and work out which offices need to be notified.' },
      { title: 'Agreement and payment', body: 'We sign an engagement agreement and you pay the annual fee of US$200.' },
      { title: 'Filing the appointment', body: 'We prepare the forms, you sign them, and we file them with the tax office, the city or ward, and the prefecture.' },
      { title: 'Notices and payments', body: 'We send each notice as a PDF, normally within 3 business days of receiving it, and pay the taxes you ask us to pay before the deadline.' },
      { title: 'Renewal or ending', body: 'The service renews every year. When you no longer need it, for example after selling the property, we file the termination.' },
    ],
    faq: [
      {
        q: 'Do I need a tax agent if I own a home in Japan but do not live here?',
        a: 'In most cases, yes. Fixed asset tax is billed every year, and if you rent the property out you also need to deal with income tax. Japanese law generally expects owners with no address in Japan to appoint a tax agent and notify the tax office and local governments.',
      },
      {
        q: 'How much does it cost?',
        a: 'US$200 a year, paid one year in advance by Wise (US dollars) or USDC. Transfer fees are paid by you. The fee does not depend on where in Japan the property is.',
      },
      {
        q: 'Can you prepare my tax return?',
        a: 'No. Preparing and filing tax returns and giving tax advice are reserved for licensed tax accountants (zeirishi) in Japan. Please file yourself or hire a licensed tax accountant.',
      },
      {
        q: 'If a tax goes unpaid, do you pay it?',
        a: 'No. You remain the taxpayer, and we never pay taxes out of our own funds. We pay only what you have sent us in advance.',
      },
      {
        q: 'Will the tax notices be in English?',
        a: 'No, Japanese tax notices are in Japanese. When we forward them, we add a short note in English on what each document is, the amount and the due date. This is not tax advice.',
      },
      {
        q: 'Can a friend or relative in Japan be my tax agent instead?',
        a: 'Yes. No licence is needed. Owners usually choose a company when they have no one in Japan they can ask, or would rather not rely on a friend for years.',
      },
    ],
    ctaTitle: 'Ask about the tax agent service',
    articleSlug: 'nozei-kanrinin',
  };
}
