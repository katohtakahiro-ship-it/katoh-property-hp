// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  // 独自ドメイン（Cloudflare Registrar で取得済み）。src/config/site.ts の url と揃える
  site: 'https://katohpm.com',
  trailingSlash: 'ignore',
});
