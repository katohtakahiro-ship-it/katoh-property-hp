// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  // TODO: 独自ドメイン取得後に変更（src/config/site.ts の url も合わせる）
  site: 'https://katoh-property-hp.pages.dev',
  trailingSlash: 'ignore',
});
