/**
 * 問い合わせフォームの項目定義（日英共通）。
 * フォーム画面（src/components/ContactForm.astro）と送信処理（functions/api/contact.ts）の両方が参照する。
 * 項目を変えるときはここだけ直す。
 */
export type Locale = 'ja' | 'en';
type L = Record<Locale, string>;

export const INQUIRY_TYPES = ['rent', 'buy', 'sell', 'lease', 'other'] as const;
export type InquiryType = (typeof INQUIRY_TYPES)[number];

export const TYPE_LABEL: Record<InquiryType, L> = {
  rent: { ja: '借りたい（お部屋探し）', en: 'I want to rent' },
  buy: { ja: '買いたい', en: 'I want to buy' },
  sell: { ja: '売りたい（査定・売却相談）', en: 'I want to sell' },
  lease: { ja: '貸したい（オーナー様の借主募集）', en: 'I am a landlord (tenant recruitment)' },
  other: { ja: 'その他', en: 'Other' },
};

export interface Option {
  value: string;
  label: L;
}

export interface FieldDef {
  name: string;
  label: L;
  kind: 'text' | 'email' | 'tel' | 'url' | 'select' | 'textarea' | 'radio' | 'checkbox';
  required?: boolean;
  /** 指定した相談種類のときだけ表示・必須にする。未指定なら共通 */
  for?: readonly InquiryType[];
  /** 英語フォームだけに出す */
  enOnly?: boolean;
  options?: readonly Option[];
  placeholder?: L;
  hint?: L;
  autocomplete?: string;
  maxLength?: number;
}

const opt = (value: string, ja: string, en: string): Option => ({ value, label: { ja, en } });

/** 表示順。共通項目 → 種類別 → 末尾の共通項目 */
export const FIELDS: readonly FieldDef[] = [
  { name: 'name', label: { ja: 'お名前', en: 'Name' }, kind: 'text', required: true, autocomplete: 'name', placeholder: { ja: '山田 太郎', en: 'Jane Smith' }, maxLength: 100 },
  { name: 'email', label: { ja: 'メールアドレス', en: 'Email' }, kind: 'email', required: true, autocomplete: 'email', placeholder: { ja: 'example@email.com', en: 'you@example.com' }, maxLength: 200 },
  {
    name: 'contact_method',
    label: { ja: '希望の連絡方法', en: 'Preferred way to reply' },
    kind: 'radio',
    required: true,
    options: [opt('email', 'メール', 'Email'), opt('line', 'LINE', 'LINE')],
    hint: { ja: 'LINE をご希望の方には、受付メールで友だち追加の URL をお送りします', en: 'If you choose LINE, the confirmation email will include a link to add us.' },
  },
  {
    name: 'tel',
    label: { ja: '電話番号（任意）', en: 'Phone (optional)' },
    kind: 'tel',
    autocomplete: 'tel',
    placeholder: { ja: '090-0000-0000', en: '+81 90-0000-0000' },
    hint: { ja: 'お電話での連絡をご希望の方のみ', en: 'Only if you would like us to call you.' },
    maxLength: 30,
  },

  // 英語版のみ
  {
    name: 'residence',
    label: { ja: '現在の居住地', en: 'Where do you live now?' },
    kind: 'select',
    enOnly: true,
    options: [opt('japan', '日本国内', 'In Japan'), opt('abroad', '海外', 'Outside Japan')],
  },
  {
    name: 'visa',
    label: { ja: '在留資格・在留期間（任意）', en: 'Residence status and period (optional)' },
    kind: 'text',
    enOnly: true,
    placeholder: { ja: '', en: 'e.g. Engineer/Specialist in Humanities, until 2028' },
    hint: { ja: '', en: 'Guarantor companies ask for this on rental applications; knowing it early helps us narrow down properties.' },
    maxLength: 100,
  },

  // 借りたい
  { name: 'area', label: { ja: '希望エリア・沿線', en: 'Preferred area or train line' }, kind: 'text', for: ['rent', 'buy'], placeholder: { ja: '例：武蔵小杉、東横線沿線', en: 'e.g. Musashikosugi, Tokyu Toyoko line' }, maxLength: 200 },
  {
    name: 'rent_budget',
    label: { ja: '家賃の上限', en: 'Maximum monthly rent' },
    kind: 'select',
    for: ['rent'],
    options: [
      opt('le80k', '〜8万円', 'Up to ¥80,000'),
      opt('le120k', '〜12万円', 'Up to ¥120,000'),
      opt('le150k', '〜15万円', 'Up to ¥150,000'),
      opt('le200k', '〜20万円', 'Up to ¥200,000'),
      opt('le300k', '〜30万円', 'Up to ¥300,000'),
      opt('gt300k', '30万円以上', 'Over ¥300,000'),
    ],
  },
  {
    name: 'layout',
    label: { ja: '間取り', en: 'Layout' },
    kind: 'select',
    for: ['rent'],
    options: [opt('1r-1k', '1R〜1K', '1R to 1K (studio)'), opt('1ldk', '1LDK', '1LDK'), opt('2ldk', '2LDK', '2LDK'), opt('3ldk+', '3LDK以上', '3LDK or larger')],
  },
  {
    name: 'move_in',
    label: { ja: '入居希望時期', en: 'When do you want to move in?' },
    kind: 'select',
    for: ['rent'],
    options: [opt('asap', 'すぐ', 'As soon as possible'), opt('1m', '1ヶ月以内', 'Within 1 month'), opt('2-3m', '2〜3ヶ月以内', 'Within 2 to 3 months'), opt('tbd', '未定', 'Not decided')],
  },

  // 買いたい
  {
    name: 'property_type',
    label: { ja: '物件種別', en: 'Property type' },
    kind: 'select',
    for: ['buy', 'sell'],
    options: [opt('mansion', 'マンション', 'Condominium'), opt('house', '一戸建て', 'House'), opt('land', '土地', 'Land')],
  },
  {
    name: 'budget',
    label: { ja: '予算', en: 'Budget' },
    kind: 'select',
    for: ['buy'],
    options: [
      opt('le30m', '〜3,000万円', 'Up to ¥30 million'),
      opt('le50m', '〜5,000万円', 'Up to ¥50 million'),
      opt('le70m', '〜7,000万円', 'Up to ¥70 million'),
      opt('le100m', '〜1億円', 'Up to ¥100 million'),
      opt('gt100m', '1億円以上', 'Over ¥100 million'),
    ],
  },
  {
    name: 'buy_timing',
    label: { ja: '購入の時期感', en: 'When do you plan to buy?' },
    kind: 'select',
    for: ['buy'],
    options: [opt('asap', 'すぐ', 'As soon as possible'), opt('6m', '半年以内', 'Within 6 months'), opt('1y', '1年以内', 'Within a year'), opt('research', '情報収集中', 'Just researching')],
  },
  {
    name: 'property_url',
    label: { ja: '気になっている物件の URL（任意）', en: 'Link to a property you are interested in (optional)' },
    kind: 'url',
    for: ['rent', 'buy'],
    placeholder: { ja: 'https://', en: 'https://' },
    hint: { ja: 'ポータルサイトで見つけた物件も、扱えるかどうか確認します', en: 'We will check whether we can handle a property you found on a portal site.' },
    maxLength: 500,
  },

  // 売りたい
  { name: 'location', label: { ja: '物件の所在地', en: 'Property location' }, kind: 'text', for: ['sell', 'lease'], placeholder: { ja: '例：川崎市中原区小杉町（番地は任意）', en: 'e.g. Kosugi-cho, Nakahara-ku, Kawasaki (street number optional)' }, maxLength: 200 },
  { name: 'building_name', label: { ja: 'マンション名（任意）', en: 'Building name (optional)' }, kind: 'text', for: ['sell'], maxLength: 100 },
  {
    name: 'sell_timing',
    label: { ja: '売却の時期感', en: 'When do you plan to sell?' },
    kind: 'select',
    for: ['sell'],
    options: [opt('asap', 'すぐ', 'As soon as possible'), opt('6m', '半年以内', 'Within 6 months'), opt('valuation', '未定・まず査定だけ', 'Not decided, valuation only')],
  },

  // 貸したい（オーナー）
  {
    name: 'lease_kind',
    label: { ja: '物件種別と戸数', en: 'Property type and number of units' },
    kind: 'select',
    for: ['lease'],
    options: [opt('unit', '区分（1室）', 'Single unit'), opt('units', '区分（複数室）', 'Several units'), opt('building', '一棟', 'Whole building'), opt('house', '一戸建て', 'House')],
    hint: { ja: '借主募集は川崎市中原区・幸区・川崎区の物件を対象にしています', en: 'Tenant recruitment is available for properties in Nakahara-ku, Saiwai-ku and Kawasaki-ku, Kawasaki City.' },
  },
  {
    name: 'lease_status',
    label: { ja: '現在の状況', en: 'Current status' },
    kind: 'select',
    for: ['lease'],
    options: [opt('vacant', '空室', 'Vacant'), opt('leaving', '入居中で退去予定', 'Occupied, tenant leaving'), opt('new', '新築・取得予定', 'New or to be acquired')],
  },

  // 末尾の共通項目
  { name: 'message', label: { ja: 'ご要望・メッセージ（任意）', en: 'Message (optional)' }, kind: 'textarea', placeholder: { ja: 'ご希望の条件やご質問など', en: 'Conditions, questions, anything else' }, maxLength: 3000 },
  {
    name: 'source',
    label: { ja: '当社を知ったきっかけ（任意）', en: 'How did you find us? (optional)' },
    kind: 'select',
    options: [
      opt('search', '検索（Google など）', 'Web search (Google etc.)'),
      opt('ai', 'AI（ChatGPT など）', 'AI assistant (ChatGPT etc.)'),
      opt('youtube', 'YouTube 加藤トラベル', 'YouTube (Katoh Travel)'),
      opt('referral', 'ご紹介', 'Referral'),
      opt('other', 'その他', 'Other'),
    ],
  },
  {
    name: 'agree',
    label: { ja: '個人情報の取り扱いに同意する', en: 'I agree to the privacy policy' },
    kind: 'checkbox',
    required: true,
  },
];

/** 送信処理で値をラベルに戻す */
export function optionLabel(field: FieldDef, value: string, locale: Locale): string {
  const o = field.options?.find((x) => x.value === value);
  return o ? o.label[locale] : value;
}

/** その相談種類・言語で表示される項目か */
export function isVisible(field: FieldDef, type: InquiryType, locale: Locale): boolean {
  if (field.enOnly && locale !== 'en') return false;
  if (field.for && !field.for.includes(type)) return false;
  return true;
}
