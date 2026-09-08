// @ts-check
import { defineConfig } from 'astro/config';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // 独自ドメイン（Cloudflare Registrar で取得済み）。src/config/site.ts の url と揃える
  site: 'https://katohpm.com',

  trailingSlash: 'ignore',

  // 日本語が既定（接頭辞なし）、英語は /en/ 配下（src/pages/en/）
  i18n: {
    defaultLocale: 'ja',
    locales: ['ja', 'en'],
    routing: { prefixDefaultLocale: false },
  },

  integrations: [
    sitemap({
      // サイトマップにも hreflang を出す
      i18n: {
        defaultLocale: 'ja',
        locales: { ja: 'ja-JP', en: 'en-US' },
      },
    }),
  ],
});