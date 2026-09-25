/**
 * 問い合わせフォームの送信処理（Cloudflare Pages Functions）。
 * POST /api/contact
 * - 入力検証、ハニーポット、Turnstile（TURNSTILE_SECRET_KEY がある時だけ）
 * - Resend で info@ へ通知メール、送信者へ受付メール（自動返信）
 *
 * 環境変数（Cloudflare Pages → 設定 → 変数とシークレット）:
 *   RESEND_API_KEY        必須。Resend の API キー
 *   TURNSTILE_SECRET_KEY  任意。設定すると Turnstile を検証する
 *   CONTACT_TO            任意。通知先（既定 info@katohpm.com）
 *   LINE_URL              任意。LINE 公式アカウントの友だち追加 URL（受付メールに載せる）
 */
import { FIELDS, INQUIRY_TYPES, TYPE_LABEL, isVisible, optionLabel, type InquiryType, type Locale } from '../../src/lib/contact-fields';

/** Cloudflare Pages Functions のハンドラ型（DOM の型と衝突しないよう最小限を自前で定義） */
type PagesFunction<E> = (context: { request: Request; env: E }) => Promise<Response> | Response;

interface Env {
  RESEND_API_KEY?: string;
  TURNSTILE_SECRET_KEY?: string;
  CONTACT_TO?: string;
  LINE_URL?: string;
}

const COMPANY = {
  ja: '合同会社加藤プロパティマネジメント',
  en: 'Katoh Property Management LLC',
  short: { ja: '加藤プロパティマネジメント', en: 'Katoh Property Management' },
  from: 'info@katohpm.com',
  site: 'https://katohpm.com',
  license: { ja: '宅地建物取引業 神奈川県知事（2）第30531号', en: 'Licensed real estate broker: Kanagawa Prefecture Governor (2) No. 30531' },
  address: { ja: '〒211-0025 神奈川県川崎市中原区木月4-51-1', en: '4-51-1 Kizuki, Nakahara-ku, Kawasaki, Kanagawa 211-0025, Japan' },
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });

const wantsJson = (req: Request) => (req.headers.get('accept') ?? '').includes('application/json');

const clean = (v: FormDataEntryValue | null, max = 3000) =>
  typeof v === 'string' ? v.replace(/\r\n?/g, '\n').trim().slice(0, max) : '';

const isEmail = (s: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) && s.length <= 200;

async function verifyTurnstile(secret: string, token: string, ip: string | null): Promise<boolean> {
  if (!token) return false;
  const body = new URLSearchParams({ secret, response: token });
  if (ip) body.set('remoteip', ip);
  const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body });
  const data = (await res.json().catch(() => ({}))) as { success?: boolean };
  return data.success === true;
}

async function sendEmail(apiKey: string, msg: { from: string; to: string[]; subject: string; text: string; reply_to?: string }) {
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
    body: JSON.stringify(msg),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`Resend ${res.status}: ${detail.slice(0, 300)}`);
  }
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const form = await request.formData().catch(() => null);
  if (!form) return json({ ok: false, error: 'Bad request' }, 400);

  const locale: Locale = clean(form.get('lang'), 2) === 'en' ? 'en' : 'ja';
  const ja = locale === 'ja';
  const errRequired = ja ? '必須項目を入力してください。' : 'Please fill in the required fields.';

  // ハニーポット
  if (clean(form.get('company_url'), 500)) return json({ ok: true }); // ボットには成功したふりをする

  // 種類
  const type = clean(form.get('type'), 20) as InquiryType;
  if (!INQUIRY_TYPES.includes(type)) return json({ ok: false, error: errRequired }, 400);

  // 値の収集と検証
  const values: Record<string, string> = {};
  for (const f of FIELDS) {
    if (!isVisible(f, type, locale)) continue;
    const raw = clean(form.get(f.name), f.maxLength ?? 3000);
    if (f.required && !raw) return json({ ok: false, error: errRequired }, 400);
    if (f.kind === 'email' && raw && !isEmail(raw)) {
      return json({ ok: false, error: ja ? 'メールアドレスの形式を確認してください。' : 'Please check the email address.' }, 400);
    }
    if (f.kind === 'select' && raw && !f.options?.some((o) => o.value === raw)) continue;
    values[f.name] = raw;
  }

  // Turnstile
  if (env.TURNSTILE_SECRET_KEY) {
    const token = clean(form.get('cf-turnstile-response'), 5000);
    if (!token) return json({ ok: false, error: ja ? '「私はロボットではありません」にチェックを入れてから送信してください。' : 'Please tick the "I am not a robot" box before sending.' }, 400);
    const ok = await verifyTurnstile(env.TURNSTILE_SECRET_KEY, token, request.headers.get('cf-connecting-ip'));
    if (!ok) return json({ ok: false, error: ja ? '認証に失敗しました。ページを再読み込みしてお試しください。' : 'Verification failed. Please reload the page and try again.' }, 400);
  }

  if (!env.RESEND_API_KEY) return json({ ok: false, error: ja ? '送信設定が未完了です。' : 'Sending is not configured yet.' }, 500);

  // 本文
  const lines: string[] = [];
  lines.push(`${ja ? 'ご相談の種類' : 'Type'}: ${TYPE_LABEL[type][locale]}`);
  for (const f of FIELDS) {
    if (!isVisible(f, type, locale) || f.kind === 'checkbox') continue;
    const v = values[f.name];
    if (!v) continue;
    const shown = f.kind === 'select' || f.kind === 'radio' ? optionLabel(f, v, locale) : v;
    lines.push(`${f.label[locale].replace(/（任意）|\s\(optional\)/, '')}: ${shown}`);
  }
  const summary = lines.join('\n');
  const name = values.name;
  const email = values.email;
  const to = env.CONTACT_TO || COMPANY.from;
  const fromHeader = `${COMPANY.short[locale]} <${COMPANY.from}>`;
  const typeTag = ja ? `【${TYPE_LABEL[type].ja.replace(/（.*）/, '')}】` : `[${TYPE_LABEL[type].en}]`;

  const meta = [
    `${ja ? '言語' : 'Language'}: ${locale}`,
    `${ja ? '受信日時' : 'Received'}: ${new Date().toLocaleString(ja ? 'ja-JP' : 'en-US', { timeZone: 'Asia/Tokyo' })} (JST)`,
    `IP: ${request.headers.get('cf-connecting-ip') ?? '-'} / ${request.headers.get('cf-ipcountry') ?? '-'}`,
  ].join('\n');

  const notify = {
    from: fromHeader,
    to: [to],
    reply_to: email,
    subject: `${typeTag}${name}${ja ? '様' : ''} ${ja ? 'からのお問い合わせ' : 'sent an inquiry'}`,
    text: `${ja ? 'サイトの問い合わせフォームから送信されました。このメールに返信すると送信者に届きます。' : 'Sent from the website contact form. Replying to this email reaches the sender.'}\n\n${summary}\n\n---\n${meta}`,
  };

  const lineBlock =
    values.contact_method === 'line' && env.LINE_URL
      ? ja
        ? `\n\nLINE でのご連絡をご希望とのことですので、下記から友だち追加をお願いします。追加後にお名前をお送りいただければ、LINE でご返信します。\n${env.LINE_URL}`
        : `\n\nYou chose LINE as your preferred way to reply. Please add us from the link below and send your name; we will reply on LINE.\n${env.LINE_URL}`
      : values.contact_method === 'line'
        ? ja
          ? '\n\nLINE でのご連絡をご希望とのことですので、返信メールで LINE の案内をお送りします。'
          : '\n\nYou chose LINE as your preferred way to reply. We will send you the LINE details in our reply.'
        : '';

  const autoReply = ja
    ? {
        subject: `お問い合わせを受け付けました｜${COMPANY.short.ja}`,
        text: `${name} 様\n\nお問い合わせありがとうございます。${COMPANY.ja}の加藤です。\n以下の内容で受け付けました。3営業日以内にご返信します。${lineBlock}\n\n――― お問い合わせ内容 ―――\n${summary}\n――――――――――――――\n\n来店は不要です。ヒアリングと契約手続きはオンラインで進め、内見は現地でご案内します。\nこのメールに心当たりがない場合は、お手数ですが破棄してください。\n\n${COMPANY.ja}\n${COMPANY.license.ja}\n${COMPANY.address.ja}\n${COMPANY.site}`,
      }
    : {
        subject: `We received your inquiry | ${COMPANY.short.en}`,
        text: `Dear ${name},\n\nThank you for contacting ${COMPANY.en}. This is Takahiro Katoh.\nWe have received the details below and will reply within 3 business days.${lineBlock}\n\n--- Your inquiry ---\n${summary}\n--------------------\n\nNo office visit is needed; consultations and paperwork are handled online, and viewings take place on site.\nIf you did not send this inquiry, please disregard this email.\n\n${COMPANY.en}\n${COMPANY.license.en}\n${COMPANY.address.en}\n${COMPANY.site}/en/`,
      };

  try {
    await sendEmail(env.RESEND_API_KEY, notify);
    // 受付メールは失敗しても問い合わせ自体は成立させる
    await sendEmail(env.RESEND_API_KEY, { from: fromHeader, to: [email], reply_to: COMPANY.from, ...autoReply }).catch((e) => console.error('auto-reply failed', e));
  } catch (e) {
    console.error('notify failed', e);
    return json({ ok: false, error: ja ? '送信できませんでした。時間をおいて再度お試しください。' : 'Something went wrong. Please try again later.' }, 502);
  }

  if (!wantsJson(request)) {
    return Response.redirect(new URL(ja ? '/thanks/' : '/en/thanks/', request.url).toString(), 303);
  }
  return json({ ok: true });
};

export const onRequest: PagesFunction<Env> = async ({ request }) =>
  request.method === 'POST' ? json({ ok: false, error: 'Unexpected' }, 405) : json({ ok: false, error: 'Method not allowed' }, 405);
