import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';

/**
 * ブログ記事（src/content/blog/*.md）
 * frontmatter: title / date / description / tags / faq（Q&A配列）
 * faq は記事ページ末尾の FAQ ブロックと FAQPage JSON-LD の両方に使われる。
 */
const blog = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/content/blog' }),
  schema: z.object({
    /** URL 用スラッグ。ファイル名と一致させる（Sveltia CMS が {{fields.page_slug}} でファイル名を決める。frontmatter の slug は Astro が ID に使うので使わない） */
    page_slug: z.string().optional(),
    title: z.string(),
    date: z.coerce.date(),
    description: z.string(),
    tags: z.array(z.string()).default([]),
    faq: z
      .array(
        z.object({
          q: z.string(),
          a: z.string(),
        }),
      )
      .default([]),
    /** 更新日（任意）。JSON-LD の dateModified に使う */
    updated: z.coerce.date().optional(),
    /** true なら一覧・ビルドから除外 */
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
